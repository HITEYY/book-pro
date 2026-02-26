import re
from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

from app.models import BookContent, Chapter

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def _extract_title(soup: BeautifulSoup, fallback: str) -> str:
    for tag_name in ("h1", "h2", "h3", "title"):
        tag = soup.find(tag_name)
        if tag:
            title = _normalize_text(tag.get_text(" ", strip=True))
            if title:
                return title
    return fallback


def _extract_readable_text(soup: BeautifulSoup) -> str:
    block_selectors = "h1,h2,h3,h4,h5,h6,p,li,blockquote,pre"
    blocks = soup.select(block_selectors)
    lines: list[str] = []

    for block in blocks:
        text = _normalize_text(block.get_text(" ", strip=True))
        if text:
            lines.append(text)

    if lines:
        return "\n\n".join(lines)

    return _normalize_text(soup.get_text(" ", strip=True))


def _extract_book_title_from_metadata(book: epub.EpubBook) -> str:
    candidates: list[str] = []

    # Common metadata namespace variations used in EPUB files.
    for namespace, key in (
        ("DC", "title"),
        ("dc", "title"),
        ("DCTERMS", "title"),
        ("OPF", "title"),
        ("opf", "title"),
    ):
        try:
            entries = book.get_metadata(namespace, key)
        except Exception:  # noqa: BLE001
            continue

        for entry in entries or []:
            raw = entry[0] if isinstance(entry, tuple) and entry else entry
            if isinstance(raw, str):
                normalized = _normalize_text(raw)
                if normalized:
                    candidates.append(normalized)

    metadata = getattr(book, "metadata", None)
    if isinstance(metadata, dict):
        for namespace_payload in metadata.values():
            if not isinstance(namespace_payload, dict):
                continue
            for key, entries in namespace_payload.items():
                if str(key).lower() != "title":
                    continue
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    raw = entry[0] if isinstance(entry, tuple) and entry else entry
                    if isinstance(raw, str):
                        normalized = _normalize_text(raw)
                        if normalized:
                            candidates.append(normalized)

    raw_title = getattr(book, "title", None)
    if isinstance(raw_title, str):
        normalized = _normalize_text(raw_title)
        if normalized:
            candidates.append(normalized)

    return candidates[0] if candidates else "Unknown title"


def extract_epub_metadata_title(file_path: str | Path) -> str:
    book = epub.read_epub(str(file_path))
    return _extract_book_title_from_metadata(book)


def parse_epub(
    file_path: str | Path,
    min_words: int = 80,
    preserve_paragraphs: bool = False,
) -> BookContent:
    book = epub.read_epub(str(file_path))
    title = _extract_book_title_from_metadata(book)

    chapters: list[Chapter] = []
    chapter_index = 1

    for item in book.get_items_of_type(ITEM_DOCUMENT):
        name = item.get_name() or f"chapter-{chapter_index}"
        if "nav" in name.lower():
            continue

        soup = BeautifulSoup(item.get_content(), "html.parser")
        if preserve_paragraphs:
            text = _extract_readable_text(soup)
            word_count = len(_normalize_text(text).split())
        else:
            text = _normalize_text(soup.get_text(" ", strip=True))
            word_count = len(text.split())
        if not text:
            continue

        if word_count < min_words:
            continue

        chapter_title = _extract_title(soup, fallback=name)
        chapters.append(Chapter(index=chapter_index, title=chapter_title, text=text))
        chapter_index += 1

    if not chapters:
        raise ValueError("EPUB에서 분석 가능한 챕터 텍스트를 찾지 못했습니다.")

    return BookContent(title=title, chapters=chapters)
