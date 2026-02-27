from typing import List

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CharacterEvent(BaseModel):
    character: str = Field(default="알 수 없음", description="사건의 중심이 되는 캐릭터")
    event: str = Field(default="", description="해당 챕터에서 캐릭터에게 일어난 사건")
    impact: str = Field(default="", description="사건이 캐릭터에 준 영향")


class ChapterCharacterTrait(BaseModel):
    character: str = Field(default="알 수 없음", description="해당 챕터에 등장한 캐릭터")
    traits: List[str] = Field(default_factory=list, description="챕터 맥락에서 드러난 성격/행동 특징")
    speech_inferences: List[str] = Field(
        default_factory=list,
        description="캐릭터의 말/대사에서 추론 가능한 특징, 심리, 관계 정보",
    )


class ChapterSummary(BaseModel):
    chapter_index: int
    chapter_title: str
    summary: str
    key_events: List[str] = Field(default_factory=list)
    character_events: List[CharacterEvent] = Field(default_factory=list)
    character_traits: List[ChapterCharacterTrait] = Field(default_factory=list)


class CharacterSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(default="알 수 없음")
    age: str = Field(default="알 수 없음")
    sinsang: str = Field(
        default="알 수 없음",
        description="캐릭터의 신상(정체성/배경/사회적 위치 등)",
        validation_alias=AliasChoices("sinsang", "seonsang"),
        serialization_alias="sinsang",
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


class WritingStyleSummary(BaseModel):
    summary: str
    tone: str = Field(default="알 수 없음")
    sentence_style: str = Field(default="알 수 없음")
    diction: str = Field(default="알 수 없음")
    perspective: str = Field(default="알 수 없음")
    pacing: str = Field(default="알 수 없음")
    dialogue_style: str = Field(default="알 수 없음")
    imagery_and_devices: List[str] = Field(default_factory=list)
    continuation_guidelines: List[str] = Field(default_factory=list)


class BookSummary(BaseModel):
    book_title: str
    chapter_summaries: List[ChapterSummary] = Field(default_factory=list)
    character_summaries: List[CharacterSummary] = Field(default_factory=list)
    world_summary: WorldSummary
    writing_style: WritingStyleSummary


class SummarizeResponse(BaseModel):
    data: BookSummary


class BookUploadResponse(BaseModel):
    slug: str
    book_title: str
    chapter_count: int
    epub_path: str


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


class BookReaderChapter(BaseModel):
    index: int
    title: str
    text: str


class BookReaderResponse(BaseModel):
    slug: str
    book_title: str
    chapter_count: int
    chapters: List[BookReaderChapter] = Field(default_factory=list)


class BookReaderProgressRequest(BaseModel):
    page: int = Field(default=0, ge=0)
    total_pages: int = Field(default=1, ge=1)
    ratio: float | None = Field(default=None, ge=0.0, le=1.0)


class BookReaderProgressResponse(BaseModel):
    slug: str
    page: int = 0
    total_pages: int = 1
    ratio: float = 0.0
    updated_at: str = ""


class ProviderModelsResponse(BaseModel):
    provider: str
    models: List[str] = Field(default_factory=list)


class UploadProgressResponse(BaseModel):
    upload_id: str
    file_name: str
    book_title: str = ""
    status: str
    progress: int = 0
    stage: str = "queued"
    message: str = ""
    chapter_index: int | None = None
    chapter_total: int | None = None
    chapter_title: str | None = None
    character_index: int | None = None
    character_total: int | None = None
    character_name: str | None = None
    error: str = ""
    updated_at: str


class BookAskRequest(BaseModel):
    question: str
    mode: str = Field(default="book", description="book 또는 character")
    character_name: str | None = None
    provider: str | None = None
    api_key: str | None = None
    model: str | None = None
    language: str = "ko"


class BookAskResponse(BaseModel):
    answer: str
    mode: str
    book_title: str
    character_name: str | None = None


class AudioScriptLine(BaseModel):
    speaker: str = Field(default="narrator")
    text: str = Field(default="")


class AudioScriptPayload(BaseModel):
    title: str
    lines: List[AudioScriptLine] = Field(default_factory=list)


class AudiobookCreateRequest(BaseModel):
    provider: str | None = None
    api_key: str | None = None
    model: str | None = None
    language: str = "ko"
    target_minutes: int = Field(default=15, ge=3, le=180)
    tts_api_key: str | None = None
    tts_base_url: str | None = None
    tts_model: str | None = None
    narrator_voice: str = Field(default="Cherry")
    character_voices: dict[str, str] = Field(default_factory=dict)


class AudiobookCreateResponse(BaseModel):
    book_slug: str
    book_title: str
    script_path: str
    audio_dir: str
    final_audio_path: str
    line_count: int
