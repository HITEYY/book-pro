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


def parse_epub(file_path: str | Path, min_words: int = 80) -> BookContent:
    book = epub.read_epub(str(file_path))

    title = "Unknown title"
    titles = book.get_metadata("DC", "title")
    if titles:
        raw = titles[0][0]
        if isinstance(raw, str) and raw.strip():
            title = raw.strip()

    chapters: list[Chapter] = []
    chapter_index = 1

    for item in book.get_items_of_type(ITEM_DOCUMENT):
        name = item.get_name() or f"chapter-{chapter_index}"
        if "nav" in name.lower():
            continue

        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = _normalize_text(soup.get_text(" ", strip=True))
        if not text:
            continue

        if len(text.split()) < min_words:
            continue

        chapter_title = _extract_title(soup, fallback=name)
        chapters.append(Chapter(index=chapter_index, title=chapter_title, text=text))
        chapter_index += 1

    if not chapters:
        raise ValueError("EPUB에서 분석 가능한 챕터 텍스트를 찾지 못했습니다.")

    return BookContent(title=title, chapters=chapters)
