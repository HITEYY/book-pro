import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.epub_parser import parse_epub
from app.schemas import (
    BookDetailResponse,
    BookListResponse,
    BookSummary,
    MultiSummarizeError,
    MultiSummarizeResponse,
    SummarizeResponse,
)
from app.storage import list_books, read_book_detail, save_book_summary
from app.summarizer import MultiProviderBookSummarizer, normalize_provider

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(
    title="book-pro",
    description="EPUB 소설/서사의 챕터/캐릭터/세계관 요약 생성 API",
    version="0.3.0",
)

if (WEB_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/panel")


@app.get("/panel")
def panel() -> FileResponse:
    panel_path = WEB_DIR / "index.html"
    if not panel_path.exists():
        raise HTTPException(status_code=404, detail="웹 패널 파일이 없습니다.")
    return FileResponse(str(panel_path))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _build_summarizer(
    *,
    provider: str | None,
    api_key: str | None,
    model: str | None,
) -> MultiProviderBookSummarizer:
    settings = get_settings()
    provider_value = normalize_provider(provider or settings.default_provider)
    resolved_api_key = (api_key or "").strip() or settings.openai_api_key
    resolved_model = (model or "").strip()

    default_provider = normalize_provider(settings.default_provider)
    if not resolved_model and provider_value == default_provider:
        resolved_model = settings.default_model

    if not resolved_api_key:
        raise ValueError(
            "API key가 비어 있습니다. Web Panel에서 입력하거나 .env의 OPENAI_API_KEY를 설정하세요."
        )

    return MultiProviderBookSummarizer(
        provider=provider_value,
        api_key=resolved_api_key,
        model=resolved_model or None,
    )


async def _summarize_upload(
    file: UploadFile,
    *,
    summarizer: MultiProviderBookSummarizer,
    chapter_limit: int,
    language: str,
    output_dir: str,
) -> BookSummary:
    if not file.filename:
        raise ValueError("파일 이름이 없습니다.")

    if not file.filename.lower().endswith(".epub"):
        raise ValueError(".epub 파일만 업로드할 수 있습니다.")

    temp_path: str | None = None
    try:
        suffix = Path(file.filename).suffix or ".epub"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name

        book = parse_epub(temp_path)
        book.chapters = book.chapters[:chapter_limit]

        summary = summarizer.summarize(book, language=language)
        save_book_summary(summary, root_dir=output_dir)
        return summary
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/summaries/from-epub", response_model=SummarizeResponse)
async def summarize_from_epub(
    file: UploadFile = File(..., description="요약할 EPUB 파일"),
    provider: str | None = Form(default=None),
    api_key: str | None = Form(default=None),
    model: str | None = Form(default=None),
    language: str = Form(default="ko"),
    max_chapters: int | None = Form(default=None),
) -> SummarizeResponse:
    settings = get_settings()
    chapter_limit = max_chapters or settings.max_chapters_per_request

    try:
        summarizer = _build_summarizer(provider=provider, api_key=api_key, model=model)
        summary = await _summarize_upload(
            file,
            summarizer=summarizer,
            chapter_limit=chapter_limit,
            language=language,
            output_dir=settings.output_dir,
        )
        return SummarizeResponse(data=summary)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"요약 생성 중 오류가 발생했습니다: {exc}",
        ) from exc


@app.post("/summaries/from-epubs", response_model=MultiSummarizeResponse)
async def summarize_from_epubs(
    files: list[UploadFile] = File(..., description="요약할 EPUB 파일들"),
    provider: str | None = Form(default=None),
    api_key: str | None = Form(default=None),
    model: str | None = Form(default=None),
    language: str = Form(default="ko"),
    max_chapters: int | None = Form(default=None),
) -> MultiSummarizeResponse:
    if not files:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 파일이 필요합니다.")

    settings = get_settings()
    chapter_limit = max_chapters or settings.max_chapters_per_request

    try:
        summarizer = _build_summarizer(provider=provider, api_key=api_key, model=model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results: list[BookSummary] = []
    errors: list[MultiSummarizeError] = []

    for file in files:
        file_name = file.filename or "unknown.epub"
        try:
            summary = await _summarize_upload(
                file,
                summarizer=summarizer,
                chapter_limit=chapter_limit,
                language=language,
                output_dir=settings.output_dir,
            )
            results.append(summary)
        except Exception as exc:  # noqa: BLE001
            errors.append(MultiSummarizeError(file_name=file_name, error=str(exc)))

    return MultiSummarizeResponse(
        success_count=len(results),
        failure_count=len(errors),
        data=results,
        errors=errors,
    )


@app.get("/books", response_model=BookListResponse)
def get_books(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
) -> BookListResponse:
    settings = get_settings()
    payload = list_books(settings.output_dir, page=page, page_size=page_size)
    return BookListResponse.model_validate(payload)


@app.get("/books/{book_slug}", response_model=BookDetailResponse)
def get_book_detail(book_slug: str) -> BookDetailResponse:
    settings = get_settings()

    try:
        payload = read_book_detail(settings.output_dir, slug=book_slug)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BookDetailResponse.model_validate(payload)
