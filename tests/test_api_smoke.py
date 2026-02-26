from fastapi.testclient import TestClient

from app.main import app


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
