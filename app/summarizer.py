import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from app.models import BookContent, Chapter
from app.prompts import (
    SYSTEM_PROMPT,
    build_chapter_prompt,
    build_character_prompt,
    build_world_prompt,
)
from app.schemas import (
    BookSummary,
    ChapterSummary,
    CharacterEvent,
    CharacterSummary,
    WorldSummary,
)

_PROVIDER_ALIASES = {
    "openai": "openai",
    "open-ai": "openai",
    "open_ai": "openai",
    "anthropic": "anthropic",
    "openrouter": "openrouter",
    "open-router": "openrouter",
    "open_router": "openrouter",
    "venice": "venice",
}

_PROVIDER_BASE_URL = {
    "openai": None,
    "anthropic": "https://api.anthropic.com/v1/",
    "openrouter": "https://openrouter.ai/api/v1",
    "venice": "https://api.venice.ai/api/v1",
}

_PROVIDER_DEFAULT_MODEL = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-sonnet-4-20250514",
    "openrouter": "openai/gpt-4.1-mini",
    "venice": "venice-uncensored",
}


class _ChapterPayload(BaseModel):
    summary: str
    key_events: list[str] = Field(default_factory=list)
    character_events: list[CharacterEvent] = Field(default_factory=list)


class _CharacterPayload(BaseModel):
    characters: list[CharacterSummary] = Field(default_factory=list)


class _WorldPayload(BaseModel):
    summary: str
    settings: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)


def normalize_provider(provider: str) -> str:
    key = (provider or "").strip().lower()
    normalized = _PROVIDER_ALIASES.get(key)
    if not normalized:
        allowed = ", ".join(sorted(set(_PROVIDER_ALIASES.values())))
        raise ValueError(f"지원하지 않는 provider 입니다: {provider}. 사용 가능: {allowed}")
    return normalized


def resolve_default_model(provider: str, configured_default: str | None = None) -> str:
    if configured_default and configured_default.strip():
        return configured_default.strip()
    return _PROVIDER_DEFAULT_MODEL[provider]


def _truncate_words(text: str, max_words: int = 2200) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def _extract_content_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks)

    return ""


def _parse_json_object(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    try:
        loaded = json.loads(raw)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start : end + 1]
        loaded = json.loads(candidate)
        if isinstance(loaded, dict):
            return loaded

    raise ValueError("JSON 객체를 파싱할 수 없습니다.")


class MultiProviderBookSummarizer:
    def __init__(self, *, provider: str, api_key: str, model: str | None = None) -> None:
        self.provider = normalize_provider(provider)
        if not api_key:
            raise ValueError(f"{self.provider} provider용 API key가 비어 있습니다.")

        kwargs: dict[str, Any] = {"api_key": api_key}
        base_url = _PROVIDER_BASE_URL[self.provider]
        if base_url:
            kwargs["base_url"] = base_url

        self.client = OpenAI(**kwargs)
        self.model = (model or "").strip() or resolve_default_model(self.provider)

    def summarize(self, book: BookContent, *, language: str = "ko") -> BookSummary:
        chapter_summaries: list[ChapterSummary] = []

        for chapter in book.chapters:
            chapter_summaries.append(self._summarize_chapter(chapter, language=language))

        character_summaries = self._summarize_characters(
            book_title=book.title,
            chapter_summaries=chapter_summaries,
            language=language,
        )
        world_summary = self._summarize_world(
            book_title=book.title,
            chapter_summaries=chapter_summaries,
            language=language,
        )

        return BookSummary(
            book_title=book.title,
            chapter_summaries=chapter_summaries,
            character_summaries=character_summaries,
            world_summary=world_summary,
        )

    def _chat_json(self, user_prompt: str) -> dict[str, Any]:
        request_kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }

        if self.provider == "openai":
            request_kwargs["response_format"] = {"type": "json_object"}

        if self.provider == "openrouter":
            request_kwargs["extra_headers"] = {
                "HTTP-Referer": "http://localhost",
                "X-Title": "book-pro",
            }

        response = self.client.chat.completions.create(**request_kwargs)

        content = _extract_content_text(response.choices[0].message.content)
        return _parse_json_object(content or "{}")

    def _summarize_chapter(self, chapter: Chapter, *, language: str) -> ChapterSummary:
        prompt = build_chapter_prompt(
            chapter_title=chapter.title,
            chapter_text=_truncate_words(chapter.text, max_words=2200),
            language=language,
        )

        try:
            payload = _ChapterPayload.model_validate(self._chat_json(prompt))
        except (ValidationError, ValueError, json.JSONDecodeError):
            payload = _ChapterPayload(
                summary=_truncate_words(chapter.text, max_words=120),
                key_events=[],
                character_events=[],
            )

        return ChapterSummary(
            chapter_index=chapter.index,
            chapter_title=chapter.title,
            summary=payload.summary,
            key_events=payload.key_events,
            character_events=payload.character_events,
        )

    def _summarize_characters(
        self,
        *,
        book_title: str,
        chapter_summaries: list[ChapterSummary],
        language: str,
    ) -> list[CharacterSummary]:
        prompt = build_character_prompt(
            book_title=book_title,
            chapter_summaries=chapter_summaries,
            language=language,
        )
        try:
            payload = _CharacterPayload.model_validate(self._chat_json(prompt))
            return payload.characters
        except (ValidationError, ValueError, json.JSONDecodeError):
            return []

    def _summarize_world(
        self,
        *,
        book_title: str,
        chapter_summaries: list[ChapterSummary],
        language: str,
    ) -> WorldSummary:
        prompt = build_world_prompt(
            book_title=book_title,
            chapter_summaries=chapter_summaries,
            language=language,
        )

        try:
            payload = _WorldPayload.model_validate(self._chat_json(prompt))
            return WorldSummary(
                summary=payload.summary,
                settings=payload.settings,
                rules=payload.rules,
                themes=payload.themes,
            )
        except (ValidationError, ValueError, json.JSONDecodeError):
            fallback = "챕터 요약 기반의 세계관 정보를 파싱하지 못했습니다."
            return WorldSummary(summary=fallback, settings=[], rules=[], themes=[])
