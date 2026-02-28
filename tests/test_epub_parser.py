from bs4 import BeautifulSoup

from app.epub_parser import _extract_readable_text, _sanitize_extracted_text


def test_sanitize_extracted_text_removes_encoded_noise_token() -> None:
    noise = "aW9ReWY0ZHViS1FQUjlaZVE5SS9WUFo5TDdJWFBZd05UMFhDOGV4T3IyZENFdDc0UHNXdzBnMm14ZDVKZlpOQg"
    text = f"문장 앞 {noise} 문장 뒤"
    assert _sanitize_extracted_text(text) == "문장 앞 문장 뒤"


def test_sanitize_extracted_text_keeps_regular_content() -> None:
    text = "안녕하세요 chapter-1 sample-text 2026"
    assert _sanitize_extracted_text(text) == text


def test_extract_readable_text_ignores_encoded_noise_block() -> None:
    noise = "aW9ReWY0ZHViS1FQUjlaZVE5SS9WUFo5TDdJWFBZd05UMFhDOGV4T3IyZENFdDc0UHNXdzBnMm14ZDVKZlpOQg"
    soup = BeautifulSoup(f"<html><body><p>첫 문단</p><p>{noise}</p><p>둘째 문단</p></body></html>", "html.parser")

    assert _extract_readable_text(soup) == "첫 문단\n\n둘째 문단"
