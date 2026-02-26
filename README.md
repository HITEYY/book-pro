# book-pro

`book-pro`는 EPUB 책을 업로드하면 AI로 아래 3가지를 생성하는 API입니다.

- 챕터 요약 (`chapter_summaries`)
- 캐릭터 요약 (`character_summaries`)
- 세계관 요약 (`world_summary`)

챕터 요약에는 인물별 사건(`character_events`)이 포함됩니다.

## 1) 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`에 `OPENAI_API_KEY`를 설정하세요.
출력 경로를 바꾸고 싶으면 `BOOK_PRO_OUTPUT_DIR`를 설정하세요. 기본값은 `books`입니다.

## 2) 실행

```bash
uvicorn app.main:app --reload --port 8000
```

## 3) 사용

Swagger UI: <http://127.0.0.1:8000/docs>
Web Panel: <http://127.0.0.1:8000/panel>

또는 `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/summaries/from-epub" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/absolute/path/to/book.epub" \
  -F "provider=open-ai" \
  -F "model=gpt-4.1-mini" \
  -F "api_key=YOUR_PROVIDER_API_KEY" \
  -F "language=ko"
```

여러 권 업로드:

```bash
curl -X POST "http://127.0.0.1:8000/summaries/from-epubs" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/absolute/path/to/book1.epub" \
  -F "files=@/absolute/path/to/book2.epub" \
  -F "provider=openrouter" \
  -F "model=openai/gpt-4.1-mini" \
  -F "api_key=YOUR_PROVIDER_API_KEY" \
  -F "language=ko"
```

지원 provider:
- `open-ai`
- `anthropic`
- `openrouter`
- `venice`

웹 패널에서는 `Settings` 페이지에서 아래를 설정한 뒤 업로드할 수 있습니다.
- 기본 `Provider`
- 기본 `Model`
- 기본 `Language`
- Provider별 API Key (`OPEN-AI`, `ANTHROPIC`, `OpenRouter`, `Venice`)

## 응답 구조

```json
{
  "data": {
    "book_title": "책 제목",
    "chapter_summaries": [
      {
        "chapter_index": 1,
        "chapter_title": "챕터 제목",
        "summary": "요약",
        "key_events": ["사건"],
        "character_events": [
          {
            "character": "인물명",
            "event": "일어난 일",
            "impact": "영향"
          }
        ]
      }
    ],
    "character_summaries": [
      {
        "name": "이름",
        "age": "나이",
        "seonsang": "선상/성향",
        "growth_background": "성장 배경",
        "voice": "목소리",
        "feeling": "느낌",
        "traits": ["특징"]
      }
    ],
    "world_summary": {
      "summary": "세계관 요약",
      "settings": ["설정"],
      "rules": ["규칙"],
      "themes": ["테마"]
    }
  }
}
```

## 4) 저장 폴더 구조

요약 API 호출이 성공하면 Markdown 파일이 아래 구조로 저장됩니다.

```text
books/
  book-[책이름]/
    chapter/
      c-[챕터 숫자]-[챕터 이름].md
    character/
      [캐릭터 이름].md
    setting.md
```

예시:

```text
books/
  book-바람의 항구/
    chapter/
      c-1-서막.md
      c-2-유리 지구.md
    character/
      리나 보스.md
      룩 케인.md
    setting.md
```

## 참고

- 요약 품질은 원문 품질, 챕터 분리 상태, 선택한 모델에 따라 달라집니다.
- 매우 큰 EPUB는 비용/지연을 줄이기 위해 `max_chapters`로 제한해서 호출하세요.
