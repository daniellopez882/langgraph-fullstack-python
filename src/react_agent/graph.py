"""The agent graph.

The previous graph was:

    graph = create_react_agent(
        "anthropic:claude-3-5-haiku-latest",
        tools=[],
        prompt="You are a friendly, curious, geeky AI.",
    )

The model was hardcoded, and a template named for a "Reasoning and Action
agent (using tool calling)" was given no tools — while the project depended on
``tavily-python``. So the ReAct loop had nothing to act with, and the search
dependency was dead weight.

``build_graph`` reads the model, prompt and tools from configuration. When a
Tavily key is present the web-search tool is wired in — the agent can act. The
module still exposes ``graph`` for ``langgraph.json``; it is built from config
at import.
"""

from __future__ import annotations

from typing import Any

from langgraph.prebuilt import create_react_agent

from react_agent.config import settings


def build_tools() -> list[Any]:
    """Return the tools the agent can call (Tavily search when a key is configured)."""
    if not settings.tools_enabled:
        return []
    from langchain_community.tools.tavily_search import TavilySearchResults

    return [TavilySearchResults(max_results=settings.TAVILY_MAX_RESULTS)]


def build_graph(*, tools: list[Any] | None = None):
    """Compile the ReAct agent from configuration (``tools`` overridable for tests)."""
    return create_react_agent(
        settings.MODEL,
        tools=build_tools() if tools is None else tools,
        prompt=settings.SYSTEM_PROMPT,
    )


graph = build_graph()
