import hashlib
import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_USERS_DIR_NAME = "_users"
_USERS_STORE_FILE = "users.json"
_MIGRATED_MARKER_FILE = ".migrated"
_USER_CONTENT_DIR_NAME = "users"

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

_PBKDF2_ALGO = "pbkdf2_sha256"
_PBKDF2_ITERATIONS = 600_000


class UsernameTakenError(ValueError):
    pass


class InvalidUsernameError(ValueError):
    pass


class UserNotFoundError(ValueError):
    pass


def _users_dir(root_dir: str | Path) -> Path:
    return Path(root_dir) / _USERS_DIR_NAME


def _users_store_path(root_dir: str | Path) -> Path:
    return _users_dir(root_dir) / _USERS_STORE_FILE


def migrated_marker_path(root_dir: str | Path) -> Path:
    return _users_dir(root_dir) / _MIGRATED_MARKER_FILE


def user_content_root(root_dir: str | Path, *, user_id: str) -> Path:
    return Path(root_dir) / _USER_CONTENT_DIR_NAME / user_id


def users_store_exists(root_dir: str | Path) -> bool:
    return _users_store_path(root_dir).exists()


def _read_users_file(root_dir: str | Path) -> dict[str, Any]:
    path = _users_store_path(root_dir)
    if not path.exists():
        return {"version": 1, "users": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("users", {})
    return data


def _write_users_file(root_dir: str | Path, data: dict[str, Any]) -> None:
    users_dir = _users_dir(root_dir)
    users_dir.mkdir(parents=True, exist_ok=True)
    path = _users_store_path(root_dir)
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)


def hash_password(password: str, *, salt: str | None = None) -> tuple[str, str]:
    salt_hex = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        _PBKDF2_ITERATIONS,
    )
    return digest.hex(), salt_hex


def verify_password(password: str, *, password_hash: str, salt: str, iterations: int = _PBKDF2_ITERATIONS) -> bool:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    )
    return secrets.compare_digest(digest.hex(), password_hash)


def _strip_secrets(user: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in user.items() if k not in ("password_hash", "password_salt")}


def create_user(
    root_dir: str | Path,
    *,
    username: str,
    password: str,
    display_name: str = "",
    is_admin: bool = False,
) -> dict[str, Any]:
    if not _USERNAME_RE.match(username or ""):
        raise InvalidUsernameError("아이디는 3~32자의 영문/숫자/._- 조합이어야 합니다.")

    data = _read_users_file(root_dir)
    for existing in data["users"].values():
        if existing["username"].lower() == username.lower():
            raise UsernameTakenError(f"이미 사용 중인 아이디입니다: {username}")

    user_id = secrets.token_hex(8)
    password_hash, salt = hash_password(password)
    user = {
        "id": user_id,
        "username": username,
        "display_name": display_name or username,
        "password_hash": password_hash,
        "password_salt": salt,
        "password_algo": _PBKDF2_ALGO,
        "password_iterations": _PBKDF2_ITERATIONS,
        "is_admin": is_admin,
        "disabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "settings": {},
    }
    data["users"][user_id] = user
    _write_users_file(root_dir, data)

    user_content_root(root_dir, user_id=user_id).mkdir(parents=True, exist_ok=True)
    return user


def get_user(root_dir: str | Path, *, user_id: str) -> dict[str, Any] | None:
    data = _read_users_file(root_dir)
    return data["users"].get(user_id)


def get_user_by_username(root_dir: str | Path, *, username: str) -> dict[str, Any] | None:
    data = _read_users_file(root_dir)
    for user in data["users"].values():
        if user["username"].lower() == (username or "").lower():
            return user
    return None


def list_users(root_dir: str | Path) -> list[dict[str, Any]]:
    data = _read_users_file(root_dir)
    return [_strip_secrets(user) for user in data["users"].values()]


def set_user_password(root_dir: str | Path, *, user_id: str, new_password: str) -> None:
    data = _read_users_file(root_dir)
    user = data["users"].get(user_id)
    if user is None:
        raise UserNotFoundError(f"사용자를 찾을 수 없습니다: {user_id}")
    password_hash, salt = hash_password(new_password)
    user["password_hash"] = password_hash
    user["password_salt"] = salt
    user["password_algo"] = _PBKDF2_ALGO
    user["password_iterations"] = _PBKDF2_ITERATIONS
    _write_users_file(root_dir, data)


def set_user_disabled(root_dir: str | Path, *, user_id: str, disabled: bool) -> None:
    data = _read_users_file(root_dir)
    user = data["users"].get(user_id)
    if user is None:
        raise UserNotFoundError(f"사용자를 찾을 수 없습니다: {user_id}")
    user["disabled"] = disabled
    _write_users_file(root_dir, data)


def update_user_settings(root_dir: str | Path, *, user_id: str, settings_patch: dict[str, Any]) -> dict[str, Any]:
    data = _read_users_file(root_dir)
    user = data["users"].get(user_id)
    if user is None:
        raise UserNotFoundError(f"사용자를 찾을 수 없습니다: {user_id}")
    merged = {**user.get("settings", {}), **(settings_patch or {})}
    user["settings"] = merged
    _write_users_file(root_dir, data)
    return merged
