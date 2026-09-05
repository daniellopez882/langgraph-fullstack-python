"""Deployment auth.

The previous hook was:

    @auth.authenticate
    async def authenticate(authorization: str) -> str:
        \"\"\"Enable all users.\"\"\"
        return "default_user"

The LangGraph deployment API creates runs — paid model calls. That hook
accepted every caller and identified them all as one user, so anyone who could
reach the deployment could spend the operator's model credit, and the
per-thread ``user_id`` (a client-set cookie in the UI) was the only separation.

The permissive path stays as the documented **development** default, because a
langgraph-cli dev server on localhost wants it. But when ``AUTH_TOKEN`` is set,
the ``Authorization: Bearer <token>`` header is required and compared in
constant time; a caller without it is rejected. ``is_authorized`` and
``resolve_identity`` are plain functions so the behaviour is unit-tested.
"""

from __future__ import annotations

import hashlib
import hmac

from langgraph_sdk import Auth

from react_agent.config import settings

auth = Auth()

PUBLIC_USER = "public"


def _bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


def is_authorized(authorization: str | None) -> bool:
    """Whether this request may use the deployment."""
    if not settings.auth_required:
        return True
    token = _bearer(authorization)
    return token is not None and hmac.compare_digest(token, settings.AUTH_TOKEN.strip())


def resolve_identity(authorization: str | None) -> str:
    """Return a stable identity for an authorized caller.

    With a token configured, the identity is derived from it (never the token
    itself). Without one, every caller is the shared public identity — which
    is the honest label for the dev default, not "default_user".
    """
    if settings.auth_required:
        token = _bearer(authorization) or ""
        return "user_" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]
    return PUBLIC_USER


@auth.authenticate
async def authenticate(authorization: str | None = None) -> str:
    """Reject unauthorized callers when a token is configured; otherwise allow."""
    if not is_authorized(authorization):
        raise Auth.exceptions.HTTPException(
            status_code=401, detail="Invalid or missing token"
        )
    return resolve_identity(authorization)
