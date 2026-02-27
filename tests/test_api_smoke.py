import pytest
from fastapi.testclient import TestClient

from app.main import app, _is_local_tts_base_url, _resolve_chapter_parallel, _resolve_tts_api_key


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirects_to_panel() -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers.get("location") == "/panel"


def test_panel_page_is_served() -> None:
    response = client.get("/panel")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "book-pro Web Panel" in response.text


def test_skill_markdown_endpoint() -> None:
    response = client.get("/skill.md")
    assert response.status_code == 200
    assert "text/markdown" in response.headers.get("content-type", "")
    assert "# book-pro Skill" in response.text


def test_book_ask_requires_question() -> None:
    response = client.post("/books/book-missing/ask", json={"question": "   "})
    assert response.status_code == 400
    assert "질문" in response.json()["detail"]


def test_book_ask_character_requires_name() -> None:
    response = client.post(
        "/books/book-missing/ask",
        json={"question": "안녕", "mode": "character", "character_name": ""},
    )
    assert response.status_code == 400
    assert "character_name" in response.json()["detail"]


def test_create_audiobook_requires_existing_book() -> None:
    response = client.post(
        "/books/book-missing/audiobook",
        json={
            "api_key": "test-key",
            "tts_api_key": "test-tts-key",
        },
    )
    assert response.status_code == 404


def test_upload_epub_only_rejects_non_epub() -> None:
    response = client.post(
        "/books/upload-epub",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert ".epub" in response.json()["detail"]


def test_summarize_existing_book_requires_existing_book() -> None:
    response = client.post("/books/book-missing/summaries")
    assert response.status_code == 404


def test_reader_progress_requires_existing_book() -> None:
    response = client.get("/books/book-missing/reader/progress")
    assert response.status_code == 404


def test_reader_progress_update_requires_existing_book() -> None:
    response = client.put(
        "/books/book-missing/reader/progress",
        json={"page": 3, "total_pages": 20, "ratio": 0.15},
    )
    assert response.status_code == 404


def test_is_local_tts_base_url() -> None:
    assert _is_local_tts_base_url("http://127.0.0.1:8091/v1")
    assert _is_local_tts_base_url("http://localhost:8091/v1")
    assert not _is_local_tts_base_url("https://dashscope.aliyuncs.com/compatible-mode/v1")


def test_resolve_tts_api_key_uses_none_for_local_vllm() -> None:
    resolved = _resolve_tts_api_key(
        payload_tts_api_key="",
        default_tts_api_key="",
        tts_base_url="http://127.0.0.1:8091/v1",
    )
    assert resolved == "none"


def test_resolve_tts_api_key_requires_value_for_remote() -> None:
    with pytest.raises(ValueError):
        _resolve_tts_api_key(
            payload_tts_api_key="",
            default_tts_api_key="",
            tts_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )


def test_resolve_chapter_parallel_clamps_values() -> None:
    assert _resolve_chapter_parallel(None, 3) == 3
    assert _resolve_chapter_parallel(0, 3) == 1
    assert _resolve_chapter_parallel(99, 3) == 8
