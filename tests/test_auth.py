"""
Deployment auth.

The old hook returned "default_user" for every caller on a deployment that
creates paid model runs.
"""

from __future__ import annotations

import pytest

from react_agent import auth
from react_agent.config import settings


class TestPermissiveDefault:
    def test_with_no_token_configured_any_caller_is_authorized(self, monkeypatch):
        monkeypatch.setattr(settings, "AUTH_TOKEN", "")
        assert auth.is_authorized(None) is True
        assert auth.is_authorized("Bearer whatever") is True

    def test_the_shared_identity_is_labelled_public_not_default_user(self, monkeypatch):
        monkeypatch.setattr(settings, "AUTH_TOKEN", "")
        assert auth.resolve_identity(None) == "public"
        assert auth.resolve_identity("Bearer x") == "public"


class TestTokenRequired:
    @pytest.fixture(autouse=True)
    def _token(self, monkeypatch):
        monkeypatch.setattr(settings, "AUTH_TOKEN", "s3cret-token")

    def test_the_correct_bearer_token_is_authorized(self):
        assert auth.is_authorized("Bearer s3cret-token") is True

    @pytest.mark.parametrize(
        "header",
        [None, "", "s3cret-token", "Bearer wrong", "Basic s3cret-token", "Bearer"],
    )
    def test_missing_or_wrong_tokens_are_rejected(self, header):
        assert auth.is_authorized(header) is False

    def test_the_identity_is_derived_not_the_token(self):
        identity = auth.resolve_identity("Bearer s3cret-token")
        assert identity.startswith("user_")
        assert "s3cret-token" not in identity

    def test_the_same_token_gives_a_stable_identity(self):
        assert auth.resolve_identity("Bearer s3cret-token") == auth.resolve_identity(
            "Bearer s3cret-token"
        )


class TestAuthenticateHook:
    async def _call(self, header):
        return await auth.authenticate(header)

    def test_it_allows_when_permissive(self, monkeypatch):
        import asyncio

        monkeypatch.setattr(settings, "AUTH_TOKEN", "")
        assert asyncio.run(self._call(None)) == "public"

    def test_it_raises_on_a_bad_token(self, monkeypatch):
        import asyncio

        monkeypatch.setattr(settings, "AUTH_TOKEN", "s3cret-token")
        with pytest.raises(Exception):
            asyncio.run(self._call("Bearer wrong"))

    def test_it_returns_a_derived_identity_on_a_good_token(self, monkeypatch):
        import asyncio

        monkeypatch.setattr(settings, "AUTH_TOKEN", "s3cret-token")
        assert asyncio.run(self._call("Bearer s3cret-token")).startswith("user_")
