"""Configuration.

The previous code hardcoded the model (``anthropic:claude-3-5-haiku-latest``)
in graph.py, gave the "ReAct tool-calling agent" no tools while depending on
``tavily-python``, and shipped an auth hook that returned ``"default_user"``
for every caller. All three are settings now.
"""

from __future__ import annotations

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODEL = "anthropic:claude-3-5-haiku-latest"
DEFAULT_SYSTEM_PROMPT = "You are a friendly, curious, geeky AI."


class Settings(BaseSettings):
    """Runtime configuration, read from the environment or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # The chat model, as a LangChain init string ("<provider>:<model>").
    MODEL: str = DEFAULT_MODEL
    SYSTEM_PROMPT: str = DEFAULT_SYSTEM_PROMPT

    # Web search tool. Enabled when a key is present; the dependency existed but
    # the agent had no tools.
    TAVILY_API_KEY: str = ""
    TAVILY_MAX_RESULTS: int = Field(default=3, ge=1, le=10)

    # Deployment auth. Empty means the permissive dev default (any caller); set
    # it to require `Authorization: Bearer <token>` on the LangGraph API.
    AUTH_TOKEN: str = ""

    # The LangGraph server the FastHTML UI talks to.
    LANGGRAPH_URL: str = "http://127.0.0.1:2024"

    @property
    def tools_enabled(self) -> bool:
        """Whether the web-search tool should be wired into the agent."""
        return bool(self.TAVILY_API_KEY.strip())

    @property
    def auth_required(self) -> bool:
        """Whether the deployment requires a bearer token."""
        return bool(self.AUTH_TOKEN.strip())


settings = Settings()


def reload_from_env() -> Settings:
    """Rebuild settings from the current environment. Used by the tests."""
    global settings
    env_file = None if os.getenv("REACT_AGENT_NO_ENV_FILE") else ".env"
    settings = Settings(_env_file=env_file)  # type: ignore[call-arg]
    return settings
