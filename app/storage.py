import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.epub_parser import parse_epub
from app.schemas import (
    BookSummary,
    ChapterCharacterTrait,
    CharacterEvent,
    CharacterSummary,
    ChapterSummary,
)

_INVALID_CHARS_RE = re.compile(r'[\\/:*?"<>|]')
_WHITESPACE_RE = re.compile(r"\s+")
_CHAPTER_NAME_RE = re.compile(r"^c-(?P<index>\d+)-(?P<title>.+)\.md$")


def _slug_part(value: str, fallback: str) -> str:
    cleaned = _INVALID_CHARS_RE.sub("-", value or "")
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    cleaned = cleaned.strip(".-_")
    return cleaned or fallback


def _book_dir_name(book_title: str) -> str:
    return f"book-{_slug_part(book_title, 'unknown-book')}"


def _chapter_file_name(chapter: ChapterSummary) -> str:
    chapter_no = max(chapter.chapter_index, 1)
    chapter_title = _slug_part(chapter.chapter_title, f"chapter-{chapter_no}")
    return f"c-{chapter_no}-{chapter_title}.md"


def _character_file_name(character: CharacterSummary) -> str:
    return f"{_slug_part(character.name, 'unknown-character')}.md"


def _epub_file_name(original_filename: str, fallback_base: str) -> str:
    raw_stem = Path(original_filename or "").stem
    safe_stem = _slug_part(raw_stem, fallback_base)
    return f"{safe_stem}.epub"


def _render_character_events(rows: list[CharacterEvent]) -> str:
    if not rows:
        return "- 없음"

    lines: list[str] = []
    for row in rows:
        lines.append(f"- **인물**: {row.character}")
        lines.append(f"  - 사건: {row.event}")
        lines.append(f"  - 영향: {row.impact}")
    return "\n".join(lines)


def _render_chapter_markdown(chapter: ChapterSummary) -> str:
    events = "\n".join(f"- {event}" for event in chapter.key_events) if chapter.key_events else "- 없음"
    character_events = _render_character_events(chapter.character_events)
    character_traits = _render_character_traits(chapter.character_traits)

    return (
        f"# Chapter {chapter.chapter_index}: {chapter.chapter_title}\n\n"
        f"## 요약\n{chapter.summary}\n\n"
        f"## 핵심 사건\n{events}\n\n"
        f"## 캐릭터별 사건/영향\n{character_events}\n\n"
        f"## 캐릭터 특징 관찰(정밀 분석)\n{character_traits}\n"
    )


def _render_character_traits(rows: list[ChapterCharacterTrait]) -> str:
    if not rows:
        return "- 없음"

    lines: list[str] = []
    for row in rows:
        traits = ", ".join(row.traits) if row.traits else "없음"
        speech = ", ".join(row.speech_inferences) if row.speech_inferences else "없음"
        lines.append(f"- **인물**: {row.character}")
        lines.append(f"  - 특징: {traits}")
        lines.append(f"  - 대사 기반 추론: {speech}")
    return "\n".join(lines)


def _render_character_markdown(character: CharacterSummary) -> str:
    traits = "\n".join(f"- {trait}" for trait in character.traits) if character.traits else "- 없음"

    return (
        f"# {character.name}\n\n"
        f"- 나이: {character.age}\n"
        f"- 신상: {character.sinsang}\n"
        f"- 성장 배경: {character.growth_background}\n"
        f"- 목소리: {character.voice}\n"
        f"- 느낌: {character.feeling}\n\n"
        f"## 특징\n{traits}\n"
    )


def _render_setting_markdown(summary: BookSummary) -> str:
    world = summary.world_summary
    style = summary.writing_style
    settings = "\n".join(f"- {item}" for item in world.settings) if world.settings else "- 없음"
    rules = "\n".join(f"- {item}" for item in world.rules) if world.rules else "- 없음"
    themes = "\n".join(f"- {item}" for item in world.themes) if world.themes else "- 없음"
    style_devices = (
        "\n".join(f"- {item}" for item in style.imagery_and_devices)
        if style.imagery_and_devices
        else "- 없음"
    )
    continuation = (
        "\n".join(f"- {item}" for item in style.continuation_guidelines)
        if style.continuation_guidelines
        else "- 없음"
    )

    return (
        f"# {summary.book_title} 세계관 설정\n\n"
        f"## 세계관 요약\n{world.summary}\n\n"
        f"## 설정\n{settings}\n\n"
        f"## 규칙\n{rules}\n\n"
        f"## 테마\n{themes}\n\n"
        f"## 작가 필체 분석\n"
        f"- 핵심 요약: {style.summary}\n"
        f"- 톤: {style.tone}\n"
        f"- 문장 스타일: {style.sentence_style}\n"
        f"- 어휘 선택: {style.diction}\n"
        f"- 시점/서술 거리: {style.perspective}\n"
        f"- 전개 속도: {style.pacing}\n"
        f"- 대사 스타일: {style.dialogue_style}\n\n"
        f"## 이미지/수사 패턴\n{style_devices}\n\n"
        f"## 이어쓰기 가이드\n{continuation}\n"
    )


def _to_iso_utc(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def _book_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        [p for p in root.iterdir() if p.is_dir() and p.name.startswith("book-")],
        key=lambda p: p.name,
    )


def _latest_markdown_timestamp(book_dir: Path) -> float:
    md_files = list(book_dir.rglob("*.md"))
    if not md_files:
        return book_dir.stat().st_mtime
    return max(p.stat().st_mtime for p in md_files)


def _latest_epub_path(book_dir: Path) -> Path | None:
    epub_files = sorted(
        [p for p in book_dir.glob("*.epub") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not epub_files:
        return None
    return epub_files[0]


def _book_title_from_setting(book_dir: Path, fallback_slug: str) -> str:
    setting_path = book_dir / "setting.md"
    if setting_path.exists():
        first_line = setting_path.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        if first_line:
            line = first_line[0].strip()
            if line.startswith("# "):
                heading = line[2:].strip()
                suffix = " 세계관 설정"
                if heading.endswith(suffix):
                    return heading[: -len(suffix)].strip() or fallback_slug
                return heading or fallback_slug
    return fallback_slug


def list_books(root_dir: str | Path, *, page: int = 1, page_size: int = 10) -> dict:
    root = Path(root_dir)
    books = []
    for book_dir in _book_dirs(root):
        slug = book_dir.name
        display_title = slug[len("book-") :] if slug.startswith("book-") else slug
        chapter_count = len(list((book_dir / "chapter").glob("*.md")))
        character_count = len(list((book_dir / "character").glob("*.md")))
        is_completed = (book_dir / "setting.md").exists()
        latest_ts = _latest_markdown_timestamp(book_dir)
        books.append(
            {
                "slug": slug,
                "book_title": _book_title_from_setting(book_dir, display_title),
                "chapter_count": chapter_count,
                "character_count": character_count,
                "status": "completed" if is_completed else "processing",
                "updated_at": _to_iso_utc(latest_ts),
                "_latest_ts": latest_ts,
            }
        )

    books.sort(key=lambda row: row["_latest_ts"], reverse=True)
    total = len(books)

    page = max(page, 1)
    page_size = max(min(page_size, 50), 1)
    start = (page - 1) * page_size
    end = start + page_size

    page_items = []
    for row in books[start:end]:
        row.pop("_latest_ts", None)
        page_items.append(row)

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": page_items,
    }


def _safe_book_path(root: Path, slug: str) -> Path:
    if not slug or "/" in slug or "\\" in slug or ".." in slug:
        raise ValueError("유효하지 않은 책 식별자입니다.")
    book_dir = root / slug
    if not book_dir.exists() or not book_dir.is_dir():
        raise FileNotFoundError(f"책 폴더를 찾을 수 없습니다: {slug}")
    return book_dir


def _chapter_sort_key(path: Path) -> tuple[int, str]:
    match = _CHAPTER_NAME_RE.match(path.name)
    if not match:
        return (10**9, path.name)
    return (int(match.group("index")), path.name)


def read_book_detail(root_dir: str | Path, *, slug: str) -> dict:
    root = Path(root_dir)
    book_dir = _safe_book_path(root, slug)

    chapter_dir = book_dir / "chapter"
    character_dir = book_dir / "character"
    setting_path = book_dir / "setting.md"

    chapters = []
    for chapter_path in sorted(chapter_dir.glob("*.md"), key=_chapter_sort_key):
        match = _CHAPTER_NAME_RE.match(chapter_path.name)
        index = int(match.group("index")) if match else 0
        title = match.group("title") if match else chapter_path.stem
        chapters.append(
            {
                "index": index,
                "title": title,
                "file_name": chapter_path.name,
                "markdown": chapter_path.read_text(encoding="utf-8", errors="ignore"),
            }
        )

    characters = []
    for char_path in sorted(character_dir.glob("*.md"), key=lambda p: p.name):
        characters.append(
            {
                "name": char_path.stem,
                "file_name": char_path.name,
                "markdown": char_path.read_text(encoding="utf-8", errors="ignore"),
            }
        )

    setting_markdown = ""
    if setting_path.exists():
        setting_markdown = setting_path.read_text(encoding="utf-8", errors="ignore")

    latest_ts = _latest_markdown_timestamp(book_dir)
    display_title = slug[len("book-") :] if slug.startswith("book-") else slug

    return {
        "slug": slug,
        "book_title": _book_title_from_setting(book_dir, display_title),
        "updated_at": _to_iso_utc(latest_ts),
        "chapter_count": len(chapters),
        "character_count": len(characters),
        "chapters": chapters,
        "characters": characters,
        "setting_markdown": setting_markdown,
    }


def read_book_reader(root_dir: str | Path, *, slug: str) -> dict:
    root = Path(root_dir)
    book_dir = _safe_book_path(root, slug)
    epub_path = _latest_epub_path(book_dir)
    if not epub_path:
        raise FileNotFoundError(f"원문 EPUB 파일을 찾을 수 없습니다: {slug}")

    book = parse_epub(epub_path, min_words=1, preserve_paragraphs=True)
    return {
        "slug": slug,
        "book_title": book.title,
        "chapter_count": len(book.chapters),
        "chapters": [
            {
                "index": chapter.index,
                "title": chapter.title,
                "text": chapter.text,
            }
            for chapter in book.chapters
        ],
    }


def save_book_summary(summary: BookSummary, *, root_dir: str | Path = "books") -> Path:
    root = Path(root_dir)
    book_dir = root / _book_dir_name(summary.book_title)
    chapter_dir = book_dir / "chapter"
    character_dir = book_dir / "character"

    chapter_dir.mkdir(parents=True, exist_ok=True)
    character_dir.mkdir(parents=True, exist_ok=True)

    for chapter in summary.chapter_summaries:
        save_chapter_summary(summary.book_title, chapter, root_dir=root)

    for character in summary.character_summaries:
        path = character_dir / _character_file_name(character)
        path.write_text(_render_character_markdown(character), encoding="utf-8")

    setting_path = book_dir / "setting.md"
    setting_path.write_text(_render_setting_markdown(summary), encoding="utf-8")

    return book_dir


def save_chapter_summary(
    book_title: str,
    chapter: ChapterSummary,
    *,
    root_dir: str | Path = "books",
) -> Path:
    root = Path(root_dir)
    book_dir = root / _book_dir_name(book_title)
    chapter_dir = book_dir / "chapter"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapter_path = chapter_dir / _chapter_file_name(chapter)
    chapter_path.write_text(_render_chapter_markdown(chapter), encoding="utf-8")
    return chapter_path


def ensure_book_directories(book_title: str, *, root_dir: str | Path = "books") -> Path:
    root = Path(root_dir)
    book_dir = root / _book_dir_name(book_title)
    (book_dir / "chapter").mkdir(parents=True, exist_ok=True)
    (book_dir / "character").mkdir(parents=True, exist_ok=True)
    return book_dir


def save_uploaded_epub(
    book_title: str,
    *,
    source_file_path: str | Path,
    original_filename: str,
    root_dir: str | Path = "books",
) -> Path:
    book_dir = ensure_book_directories(book_title, root_dir=root_dir)
    target_name = _epub_file_name(original_filename, fallback_base=book_title or "book")
    target_path = book_dir / target_name
    shutil.copyfile(str(source_file_path), str(target_path))
    return target_path


def read_book_summary_snapshot(root_dir: str | Path, *, slug: str) -> dict:
    detail = read_book_detail(root_dir, slug=slug)
    chapter_summaries: list[ChapterSummary] = []

    for chapter in detail["chapters"]:
        summary = extract_section(chapter["markdown"], "요약")
        key_events = [
            row.strip()[2:].strip()
            for row in extract_section(chapter["markdown"], "핵심 사건").splitlines()
            if row.strip().startswith("- ")
        ]
        chapter_summaries.append(
            ChapterSummary(
                chapter_index=chapter["index"],
                chapter_title=chapter["title"],
                summary=summary or "",
                key_events=key_events,
                character_events=[],
                character_traits=[],
            )
        )

    return {
        "book_title": detail["book_title"],
        "chapter_summaries": chapter_summaries,
        "character_summaries_text": "\n\n".join(item["markdown"] for item in detail["characters"]),
        "setting_markdown": detail.get("setting_markdown", ""),
    }


def extract_section(markdown: str, section_title: str) -> str:
    pattern = rf"##\s+{re.escape(section_title)}\n([\s\S]*?)(\n##\s+|$)"
    match = re.search(pattern, markdown or "", flags=re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()
