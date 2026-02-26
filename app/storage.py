import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import BookSummary, CharacterEvent, CharacterSummary, ChapterSummary

_INVALID_CHARS_RE = re.compile(r'[\\/:*?"<>|]')
_WHITESPACE_RE = re.compile(r"\s+")
_CHAPTER_NAME_RE = re.compile(r"^c-(?P<index>\d+)-(?P<title>.+)\\.md$")


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

    return (
        f"# Chapter {chapter.chapter_index}: {chapter.chapter_title}\n\n"
        f"## 요약\n{chapter.summary}\n\n"
        f"## 핵심 사건\n{events}\n\n"
        f"## 캐릭터별 사건/영향\n{character_events}\n"
    )


def _render_character_markdown(character: CharacterSummary) -> str:
    traits = "\n".join(f"- {trait}" for trait in character.traits) if character.traits else "- 없음"

    return (
        f"# {character.name}\n\n"
        f"- 나이: {character.age}\n"
        f"- 선상: {character.seonsang}\n"
        f"- 성장 배경: {character.growth_background}\n"
        f"- 목소리: {character.voice}\n"
        f"- 느낌: {character.feeling}\n\n"
        f"## 특징\n{traits}\n"
    )


def _render_setting_markdown(summary: BookSummary) -> str:
    world = summary.world_summary
    settings = "\n".join(f"- {item}" for item in world.settings) if world.settings else "- 없음"
    rules = "\n".join(f"- {item}" for item in world.rules) if world.rules else "- 없음"
    themes = "\n".join(f"- {item}" for item in world.themes) if world.themes else "- 없음"

    return (
        f"# {summary.book_title} 세계관 설정\n\n"
        f"## 세계관 요약\n{world.summary}\n\n"
        f"## 설정\n{settings}\n\n"
        f"## 규칙\n{rules}\n\n"
        f"## 테마\n{themes}\n"
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
        latest_ts = _latest_markdown_timestamp(book_dir)
        books.append(
            {
                "slug": slug,
                "book_title": _book_title_from_setting(book_dir, display_title),
                "chapter_count": chapter_count,
                "character_count": character_count,
                "status": "completed",
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


def save_book_summary(summary: BookSummary, *, root_dir: str | Path = "books") -> Path:
    root = Path(root_dir)
    book_dir = root / _book_dir_name(summary.book_title)
    chapter_dir = book_dir / "chapter"
    character_dir = book_dir / "character"

    chapter_dir.mkdir(parents=True, exist_ok=True)
    character_dir.mkdir(parents=True, exist_ok=True)

    for chapter in summary.chapter_summaries:
        path = chapter_dir / _chapter_file_name(chapter)
        path.write_text(_render_chapter_markdown(chapter), encoding="utf-8")

    for character in summary.character_summaries:
        path = character_dir / _character_file_name(character)
        path.write_text(_render_character_markdown(character), encoding="utf-8")

    setting_path = book_dir / "setting.md"
    setting_path.write_text(_render_setting_markdown(summary), encoding="utf-8")

    return book_dir


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
