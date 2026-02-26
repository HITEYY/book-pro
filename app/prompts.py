from typing import Iterable

from app.schemas import ChapterSummary


SYSTEM_PROMPT = (
    "You are a literary analysis assistant. "
    "Always return strict JSON only, with no markdown and no extra commentary."
)


def build_chapter_prompt(*, chapter_title: str, chapter_text: str, language: str) -> str:
    return f"""
다음은 소설/서사 텍스트의 챕터 내용이다.
요약 결과는 반드시 {language}로 작성하라.

[챕터 제목]
{chapter_title}

[챕터 본문]
{chapter_text}

아래 JSON 스키마를 정확히 지켜서 반환하라.
{{
  "summary": "챕터 핵심 요약 (4~8문장)",
  "key_events": ["핵심 사건 1", "핵심 사건 2"],
  "character_events": [
    {{"character": "인물명", "event": "무슨 일이 일어났는지", "impact": "해당 인물에 준 영향"}}
  ]
}}
""".strip()


def _chapter_compact_lines(chapter_summaries: Iterable[ChapterSummary]) -> str:
    rows: list[str] = []
    for chapter in chapter_summaries:
        rows.append(
            f"챕터 {chapter.chapter_index} - {chapter.chapter_title}: {chapter.summary} | "
            f"사건={'; '.join(chapter.key_events[:5])}"
        )
    return "\n".join(rows)


def build_character_prompt(
    *,
    book_title: str,
    chapter_summaries: list[ChapterSummary],
    language: str,
) -> str:
    compact = _chapter_compact_lines(chapter_summaries)
    return f"""
책 제목: {book_title}
아래 챕터 요약을 바탕으로 캐릭터 프로필을 추출하라.
결과는 반드시 {language}로 작성하라.

[챕터 요약 모음]
{compact}

반드시 아래 JSON 형태를 지켜라.
{{
  "characters": [
    {{
      "name": "이름",
      "age": "나이 또는 추정",
      "seonsang": "선상(성향/사회적 축)",
      "growth_background": "성장 배경",
      "voice": "말투/목소리 인상",
      "feeling": "전반적 느낌",
      "traits": ["특징1", "특징2"]
    }}
  ]
}}
""".strip()


def build_world_prompt(
    *,
    book_title: str,
    chapter_summaries: list[ChapterSummary],
    language: str,
) -> str:
    compact = _chapter_compact_lines(chapter_summaries)
    return f"""
책 제목: {book_title}
아래 요약 정보를 바탕으로 세계관을 정리하라.
결과는 반드시 {language}로 작성하라.

[챕터 요약 모음]
{compact}

아래 JSON 스키마를 지켜라.
{{
  "summary": "세계관 핵심 요약 (4~8문장)",
  "settings": ["시대/장소/사회 구조"],
  "rules": ["세계관 규칙/제약"],
  "themes": ["핵심 테마"]
}}
""".strip()
