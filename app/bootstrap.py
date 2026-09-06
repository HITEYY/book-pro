import logging
import shutil
from pathlib import Path

from app import user_storage

logger = logging.getLogger("uvicorn.error")

_RESERVED_TOP_LEVEL_NAMES = {"_users", "users"}


def bootstrap_and_migrate(
    output_dir: str,
    *,
    admin_username: str,
    admin_password: str,
) -> None:
    """Idempotent first-run setup: create the first admin account (from env vars)
    and adopt any pre-existing top-level book/studio directories into that
    admin's per-user namespace, so nothing already on disk becomes inaccessible
    once per-user scoping goes live."""
    marker = user_storage.migrated_marker_path(output_dir)
    if marker.exists():
        return

    if user_storage.users_store_exists(output_dir):
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("users store already existed; no migration performed\n", encoding="utf-8")
        return

    if not admin_password:
        logger.warning(
            "BOOK_PRO_ADMIN_PASSWORD가 설정되지 않아 최초 관리자 계정을 생성하지 않았습니다. "
            "BOOK_PRO_ADMIN_USERNAME/BOOK_PRO_ADMIN_PASSWORD를 설정한 뒤 재시작하세요."
        )
        return

    admin = user_storage.create_user(
        output_dir,
        username=admin_username,
        password=admin_password,
        is_admin=True,
    )
    _adopt_existing_top_level_dirs(output_dir, admin_user_id=admin["id"])

    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(f"migrated to admin user {admin['id']}\n", encoding="utf-8")
    logger.info("[유저 시스템 초기화] 최초 관리자 계정 '%s' 생성 및 기존 데이터 이전 완료", admin_username)


def _adopt_existing_top_level_dirs(output_dir: str, *, admin_user_id: str) -> None:
    root = Path(output_dir)
    if not root.exists():
        return
    dest = user_storage.user_content_root(output_dir, user_id=admin_user_id)
    dest.mkdir(parents=True, exist_ok=True)

    for entry in root.iterdir():
        if entry.name in _RESERVED_TOP_LEVEL_NAMES:
            continue
        target = dest / entry.name
        if target.exists():
            logger.warning("[유저 시스템 초기화] 이동 건너뜀 (대상이 이미 존재함): %s", entry.name)
            continue
        shutil.move(str(entry), str(target))
