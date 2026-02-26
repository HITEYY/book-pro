import logging
import asyncio
import os
import tempfile
from typing import Any
from datetime import datetime, timezone
from pathlib import Path

from fastapi.concurrency import run_in_threadpool
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.epub_parser import parse_epub
from app.progress import (
    complete_upload_progress,
    fail_upload_progress,
    get_upload_progress,
    init_upload_progress,
    list_upload_progress,
    update_upload_progress,
)
from app.schemas import (
    BookDetailResponse,
    BookListResponse,
    BookReaderResponse,
    BookSummary,
    ChapterSummary,
    MultiSummarizeError,
    MultiSummarizeResponse,
    ProviderModelsResponse,
    SummarizeResponse,
    UploadProgressResponse,
)
from app.provider_models import fetch_provider_models
from app.storage import (
    ensure_book_directories,
    list_books,
    read_book_detail,
    read_book_reader,
    save_book_summary,
    save_chapter_summary,
    save_uploaded_epub,
)
from app.summarizer import MultiProviderBookSummarizer, normalize_provider

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"
SKILL_DOC_PATH = BASE_DIR / "SKILL.md"
logger = logging.getLogger("uvicorn.error")
DEFAULT_MULTI_SUMMARY_PARALLEL = 3

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


@app.get("/skill.md")
def skill_markdown() -> FileResponse:
    if not SKILL_DOC_PATH.exists():
        raise HTTPException(status_code=404, detail="SKILL.md 파일이 없습니다.")
    return FileResponse(str(SKILL_DOC_PATH), media_type="text/markdown; charset=utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/providers/models", response_model=ProviderModelsResponse)
def get_provider_models(
    provider: str = Form(...),
    api_key: str | None = Form(default=None),
) -> ProviderModelsResponse:
    settings = get_settings()

    try:
        normalized = normalize_provider(provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resolved_key = (api_key or "").strip()
    if not resolved_key and normalized == normalize_provider(settings.default_provider):
        resolved_key = settings.openai_api_key

    try:
        models = fetch_provider_models(normalized, api_key=resolved_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ProviderModelsResponse(provider=normalized, models=models)


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


def _normalize_error_message(exc: Exception) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    lower = text.lower()

    if "incorrect api key provided" in lower or "invalid_api_key" in lower:
        return "API key가 유효하지 않습니다. Settings에서 선택한 Provider의 API key를 확인하세요."
    if "timed out" in lower or "timeout" in lower:
        return "AI provider 응답 대기 시간이 초과되었습니다. 잠시 후 다시 시도하세요."
    if "api key가 비어 있습니다" in text:
        return text

    if len(text) > 420:
        return f"{text[:420]}..."
    return text


async def _summarize_upload(
    file: UploadFile,
    *,
    summarizer: MultiProviderBookSummarizer,
    chapter_limit: int | None,
    language: str,
    precise_analysis: bool,
    output_dir: str,
    upload_id: str | None = None,
) -> BookSummary:
    if not file.filename:
        raise ValueError("파일 이름이 없습니다.")

    if not file.filename.lower().endswith(".epub"):
        raise ValueError(".epub 파일만 업로드할 수 있습니다.")

    upload_key = (upload_id or "").strip() or None
    if upload_key:
        init_upload_progress(upload_key, file_name=file.filename)
        update_upload_progress(
            upload_key,
            status="processing",
            progress=1,
            stage="upload",
            message="업로드 파일 수신 중",
        )

    temp_path: str | None = None
    try:
        logger.info(
            "[업로드 시작] file='%s' provider='%s' model='%s' precise=%s",
            file.filename,
            summarizer.provider,
            summarizer.model,
            precise_analysis,
        )
        suffix = Path(file.filename).suffix or ".epub"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name

        if upload_key:
            update_upload_progress(
                upload_key,
                status="processing",
                progress=4,
                stage="parse",
                message="EPUB 파싱 준비 중",
            )

        summary = await run_in_threadpool(
            _summarize_from_temp_path,
            temp_path,
            file.filename,
            summarizer,
            chapter_limit,
            language,
            precise_analysis,
            output_dir,
            upload_key,
        )
        return summary
    except Exception as exc:  # noqa: BLE001
        logger.exception("[업로드 실패] file='%s'", file.filename)
        if upload_key:
            fail_upload_progress(upload_key, error=_normalize_error_message(exc))
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _summarize_from_temp_path(
    temp_path: str,
    original_filename: str,
    summarizer: MultiProviderBookSummarizer,
    chapter_limit: int | None,
    language: str,
    precise_analysis: bool,
    output_dir: str,
    upload_id: str | None,
) -> BookSummary:
    book = parse_epub(temp_path)
    logger.info(
        "[업로드 파싱 완료] file='%s' title='%s' chapters=%d",
        original_filename,
        book.title,
        len(book.chapters),
    )
    if upload_id:
        update_upload_progress(
            upload_id,
            status="processing",
            progress=6,
            stage="parse",
            message="EPUB 메타데이터/챕터 파싱 완료",
            book_title=book.title,
            chapter_total=len(book.chapters),
        )

    ensure_book_directories(book.title, root_dir=output_dir)
    saved_epub = save_uploaded_epub(
        book.title,
        source_file_path=temp_path,
        original_filename=original_filename,
        root_dir=output_dir,
    )
    logger.info(
        "[원본 EPUB 저장] file='%s' path='%s'",
        original_filename,
        saved_epub,
    )
    if upload_id:
        update_upload_progress(
            upload_id,
            status="processing",
            progress=7,
            stage="saving",
            message="원본 EPUB 저장 완료",
            book_title=book.title,
        )

    original_chapter_count = len(book.chapters)
    if chapter_limit is not None and chapter_limit > 0:
        book.chapters = book.chapters[:chapter_limit]
        if original_chapter_count != len(book.chapters):
            logger.info(
                "[챕터 제한 적용] title='%s' %d -> %d",
                book.title,
                original_chapter_count,
                len(book.chapters),
            )
    if upload_id:
        update_upload_progress(
            upload_id,
            status="processing",
            progress=8,
            stage="chapter",
            message="요약 준비 완료" if not precise_analysis else "정밀 분석 요약 준비 완료",
            chapter_total=len(book.chapters),
            book_title=book.title,
        )

    def on_progress(payload: dict[str, Any]) -> None:
        if not upload_id:
            return
        update_upload_progress(
            upload_id,
            book_title=book.title,
            **payload,
        )

    def on_chapter_summary(chapter_summary: ChapterSummary) -> None:
        chapter_path = save_chapter_summary(
            book.title,
            chapter_summary,
            root_dir=output_dir,
        )
        logger.info(
            "[챕터 파일 즉시 저장] title='%s' chapter=%d path='%s'",
            book.title,
            chapter_summary.chapter_index,
            chapter_path,
        )

    summary = summarizer.summarize(
        book,
        language=language,
        precise_analysis=precise_analysis,
        progress_callback=on_progress,
        chapter_callback=on_chapter_summary,
    )
    if upload_id:
        update_upload_progress(
            upload_id,
            status="processing",
            progress=99,
            stage="saving",
            message="요약 Markdown 저장 중",
            book_title=summary.book_title,
        )
    saved_dir = save_book_summary(summary, root_dir=output_dir)
    logger.info(
        "[업로드 완료] file='%s' title='%s' saved_dir='%s'",
        original_filename,
        summary.book_title,
        saved_dir,
    )
    if upload_id:
        complete_upload_progress(upload_id, message="요약 완료")
        update_upload_progress(upload_id, book_title=summary.book_title)
    return summary


@app.post("/summaries/from-epub", response_model=SummarizeResponse)
async def summarize_from_epub(
    file: UploadFile = File(..., description="요약할 EPUB 파일"),
    upload_id: str | None = Form(default=None),
    provider: str | None = Form(default=None),
    api_key: str | None = Form(default=None),
    model: str | None = Form(default=None),
    language: str = Form(default="ko"),
    precise_analysis: bool = Form(default=False),
    max_chapters: int | None = Form(default=None),
) -> SummarizeResponse:
    settings = get_settings()
    chapter_limit = (
        max_chapters
        if max_chapters is not None
        else settings.max_chapters_per_request
    )
    if chapter_limit is not None and chapter_limit <= 0:
        chapter_limit = None

    try:
        logger.info(
            "[요청 시작] /summaries/from-epub file='%s' precise=%s",
            file.filename or "unknown.epub",
            precise_analysis,
        )
        summarizer = _build_summarizer(provider=provider, api_key=api_key, model=model)
        summary = await _summarize_upload(
            file,
            summarizer=summarizer,
            chapter_limit=chapter_limit,
            language=language,
            precise_analysis=precise_analysis,
            output_dir=settings.output_dir,
            upload_id=upload_id,
        )
        logger.info(
            "[요청 완료] /summaries/from-epub title='%s'",
            summary.book_title,
        )
        return SummarizeResponse(data=summary)
    except ValueError as exc:
        logger.warning("[요청 오류] /summaries/from-epub error='%s'", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("[요청 실패] /summaries/from-epub")
        normalized_error = _normalize_error_message(exc)
        status_code = 400 if "API key" in normalized_error else 500
        raise HTTPException(
            status_code=status_code,
            detail=f"요약 생성 중 오류가 발생했습니다: {normalized_error}",
        ) from exc


@app.post("/summaries/from-epubs", response_model=MultiSummarizeResponse)
async def summarize_from_epubs(
    files: list[UploadFile] = File(..., description="요약할 EPUB 파일들"),
    provider: str | None = Form(default=None),
    api_key: str | None = Form(default=None),
    model: str | None = Form(default=None),
    language: str = Form(default="ko"),
    precise_analysis: bool = Form(default=False),
    max_chapters: int | None = Form(default=None),
    max_parallel: int | None = Form(default=None),
) -> MultiSummarizeResponse:
    if not files:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 파일이 필요합니다.")

    settings = get_settings()
    chapter_limit = (
        max_chapters
        if max_chapters is not None
        else settings.max_chapters_per_request
    )
    if chapter_limit is not None and chapter_limit <= 0:
        chapter_limit = None

    try:
        _build_summarizer(provider=provider, api_key=api_key, model=model)
    except ValueError as exc:
        logger.warning("[요청 오류] /summaries/from-epubs error='%s'", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results: list[BookSummary] = []
    errors: list[MultiSummarizeError] = []
    total_files = len(files)
    parallel = max_parallel or DEFAULT_MULTI_SUMMARY_PARALLEL
    parallel = max(1, min(parallel, total_files))
    logger.info(
        "[배치 요청 시작] /summaries/from-epubs files=%d parallel=%d precise=%s",
        total_files,
        parallel,
        precise_analysis,
    )

    semaphore = asyncio.Semaphore(parallel)

    async def process_file(index: int, file: UploadFile) -> tuple[BookSummary | None, MultiSummarizeError | None]:
        file_name = file.filename or "unknown.epub"
        logger.info("[배치 진행 %d/%d] file='%s' 대기", index, total_files, file_name)
        async with semaphore:
            logger.info("[배치 진행 %d/%d] file='%s' 처리 시작", index, total_files, file_name)
            try:
                summarizer = _build_summarizer(provider=provider, api_key=api_key, model=model)
                summary = await _summarize_upload(
                    file,
                    summarizer=summarizer,
                    chapter_limit=chapter_limit,
                    language=language,
                    precise_analysis=precise_analysis,
                    output_dir=settings.output_dir,
                )
                logger.info(
                    "[배치 진행 %d/%d] file='%s' 처리 완료 title='%s'",
                    index,
                    total_files,
                    file_name,
                    summary.book_title,
                )
                return summary, None
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "[배치 진행 %d/%d] file='%s' 처리 실패",
                    index,
                    total_files,
                    file_name,
                )
                return (
                    None,
                    MultiSummarizeError(
                        file_name=file_name,
                        error=_normalize_error_message(exc),
                    ),
                )

    outcomes = await asyncio.gather(
        *(process_file(index, file) for index, file in enumerate(files, start=1))
    )

    for summary, error in outcomes:
        if summary:
            results.append(summary)
        if error:
            errors.append(error)

    logger.info(
        "[배치 요청 완료] /summaries/from-epubs success=%d failure=%d",
        len(results),
        len(errors),
    )
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


@app.get("/books/{book_slug}/reader", response_model=BookReaderResponse)
def get_book_reader(book_slug: str) -> BookReaderResponse:
    settings = get_settings()

    try:
        payload = read_book_reader(settings.output_dir, slug=book_slug)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BookReaderResponse.model_validate(payload)


@app.get("/uploads/{upload_id}/progress", response_model=UploadProgressResponse)
def get_upload_progress_state(upload_id: str) -> UploadProgressResponse:
    payload = get_upload_progress(upload_id)
    if not payload:
        return UploadProgressResponse(
            upload_id=upload_id,
            file_name="",
            book_title="",
            status="queued",
            progress=0,
            stage="queued",
            message="요약 요청 대기 중",
            chapter_index=None,
            chapter_total=None,
            chapter_title=None,
            character_index=None,
            character_total=None,
            character_name=None,
            error="",
            updated_at=datetime.now(tz=timezone.utc).isoformat(),
        )
    return UploadProgressResponse.model_validate(payload)


@app.get("/uploads/active", response_model=list[UploadProgressResponse])
def list_active_upload_progress() -> list[UploadProgressResponse]:
    rows = list_upload_progress(active_only=True)
    return [UploadProgressResponse.model_validate(row) for row in rows]
