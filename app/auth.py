import contextvars
import logging
import secrets
from contextlib import contextmanager
from typing import Any

from fastapi import Depends, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, RedirectResponse

from app import user_storage
from app.config import get_settings

logger = logging.getLogger("uvicorn.error")


def resolve_session_secret(configured: str) -> str:
    """Returns the configured session secret, or a random per-process one as a
    fallback (existing sessions won't survive a restart in that case). This is
    pure/import-safe: it never touches disk, so importing app.main has no
    filesystem side effects regardless of what BOOK_PRO_OUTPUT_DIR resolves to."""
    if configured:
        return configured

    logger.warning(
        "BOOK_PRO_SESSION_SECRET가 설정되지 않아 임시 세션 비밀키를 사용합니다 (재시작 시 기존 로그인 세션이 무효화됩니다). "
        "프로덕션/Docker 배포에서는 BOOK_PRO_SESSION_SECRET을 직접 지정하는 것을 권장합니다."
    )
    return secrets.token_hex(32)


_current_user_ctx: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    "current_user", default=None
)
_current_root_dir_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_root_dir", default=None
)

PUBLIC_EXACT_PATHS = {"/", "/login", "/health", "/auth/login", "/skill.md"}
PUBLIC_PATH_PREFIXES = ("/static/",)

_HTML_GATED_PATHS = {"/panel", "/studio"}


def _public_path_prefixes() -> tuple[str, ...]:
    from app.mcp_server import mcp_mount_path  # local import: avoids service<->auth<->mcp_server cycle

    return PUBLIC_PATH_PREFIXES + (mcp_mount_path(),)


def get_current_root_dir() -> str:
    """Per-request storage root override. Falls back to the global configured
    output_dir when there is no logged-in user in context (e.g. MCP calls)."""
    override = _current_root_dir_ctx.get()
    return override if override is not None else get_settings().output_dir


@contextmanager
def _request_context(user: dict[str, Any] | None):
    """Sets the current-user/root-dir contextvars for the duration of the
    block and always restores their prior values afterward via the tokens
    returned by ContextVar.set(). This matters beyond tidiness: BaseHTTPMiddleware
    and TestClient transports can run unrelated requests on the same ambient
    context, so a plain `.set()` with no matching `.reset()` would leave a
    stale logged-in user visible to later code that never goes through this
    middleware at all (e.g. an in-process MCP tool call)."""
    if user is not None:
        root = str(user_storage.user_content_root(get_settings().output_dir, user_id=user["id"]))
    else:
        root = None
    user_token = _current_user_ctx.set(user)
    root_token = _current_root_dir_ctx.set(root)
    try:
        yield
    finally:
        _current_user_ctx.reset(user_token)
        _current_root_dir_ctx.reset(root_token)


class AuthGateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in PUBLIC_EXACT_PATHS or any(path.startswith(p) for p in _public_path_prefixes()):
            with _request_context(None):
                return await call_next(request)

        user_id = request.session.get("user_id")
        settings = get_settings()
        user = user_storage.get_user(settings.output_dir, user_id=user_id) if user_id else None
        if user is None or user.get("disabled"):
            with _request_context(None):
                if path in _HTML_GATED_PATHS:
                    return RedirectResponse(url=f"/login?next={path}", status_code=302)
                return JSONResponse({"detail": "로그인이 필요합니다."}, status_code=401)

        with _request_context(user):
            return await call_next(request)


async def get_current_user() -> dict[str, Any]:
    user = _current_user_ctx.get()
    if user is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user


async def require_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")
    return user
