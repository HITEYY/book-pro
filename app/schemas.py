from typing import List

from pydantic import BaseModel, Field


class CharacterEvent(BaseModel):
    character: str = Field(default="알 수 없음", description="사건의 중심이 되는 캐릭터")
    event: str = Field(default="", description="해당 챕터에서 캐릭터에게 일어난 사건")
    impact: str = Field(default="", description="사건이 캐릭터에 준 영향")


class ChapterSummary(BaseModel):
    chapter_index: int
    chapter_title: str
    summary: str
    key_events: List[str] = Field(default_factory=list)
    character_events: List[CharacterEvent] = Field(default_factory=list)


class CharacterSummary(BaseModel):
    name: str = Field(default="알 수 없음")
    age: str = Field(default="알 수 없음")
    seonsang: str = Field(
        default="알 수 없음",
        description="요청의 '선상' 항목을 성향/사회적 축으로 해석한 값",
    )
    growth_background: str = Field(default="알 수 없음")
    voice: str = Field(default="알 수 없음")
    feeling: str = Field(default="알 수 없음")
    traits: List[str] = Field(default_factory=list)


class WorldSummary(BaseModel):
    summary: str
    settings: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)


class BookSummary(BaseModel):
    book_title: str
    chapter_summaries: List[ChapterSummary] = Field(default_factory=list)
    character_summaries: List[CharacterSummary] = Field(default_factory=list)
    world_summary: WorldSummary


class SummarizeResponse(BaseModel):
    data: BookSummary


class MultiSummarizeError(BaseModel):
    file_name: str
    error: str


class MultiSummarizeResponse(BaseModel):
    success_count: int
    failure_count: int
    data: List[BookSummary] = Field(default_factory=list)
    errors: List[MultiSummarizeError] = Field(default_factory=list)


class BookListItem(BaseModel):
    slug: str
    book_title: str
    chapter_count: int
    character_count: int
    status: str
    updated_at: str


class BookListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[BookListItem] = Field(default_factory=list)


class BookChapterFile(BaseModel):
    index: int
    title: str
    file_name: str
    markdown: str


class BookCharacterFile(BaseModel):
    name: str
    file_name: str
    markdown: str


class BookDetailResponse(BaseModel):
    slug: str
    book_title: str
    updated_at: str
    chapter_count: int
    character_count: int
    chapters: List[BookChapterFile] = Field(default_factory=list)
    characters: List[BookCharacterFile] = Field(default_factory=list)
    setting_markdown: str = ""


class ProviderModelsResponse(BaseModel):
    provider: str
    models: List[str] = Field(default_factory=list)
