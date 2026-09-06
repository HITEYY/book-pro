from pathlib import Path

import pytest

from app import user_storage
from app.config import get_settings

ADMIN_USERNAME = "test-admin"
ADMIN_PASSWORD = "test-password-123"


@pytest.fixture
def make_admin(tmp_path, monkeypatch):
    """Sets BOOK_PRO_OUTPUT_DIR to an isolated tmp_path for the test and returns
    a `make_admin(client)` helper that creates (once) an admin user in that
    tmp_path, logs the given TestClient's session in as that admin, and
    returns the admin's per-user content root Path (where files created via
    the API actually land, since storage is now scoped under
    <output_dir>/users/<user_id>/ rather than <output_dir> directly)."""
    monkeypatch.setenv("BOOK_PRO_OUTPUT_DIR", str(tmp_path))
    get_settings.cache_clear()

    def _make_admin(client) -> Path:
        user = user_storage.get_user_by_username(str(tmp_path), username=ADMIN_USERNAME)
        if user is None:
            user = user_storage.create_user(
                str(tmp_path), username=ADMIN_USERNAME, password=ADMIN_PASSWORD, is_admin=True
            )
        response = client.post("/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        assert response.status_code == 200, response.text
        return user_storage.user_content_root(str(tmp_path), user_id=user["id"])

    yield _make_admin
    get_settings.cache_clear()
