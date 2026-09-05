# ADR 0001 — The model, the tools and the auth are configuration, not constants

**Status:** accepted

## Context

Three things were baked into the code:

- `graph.py` hardcoded `create_react_agent("anthropic:claude-3-5-haiku-latest", tools=[], ...)`. A template named for a "Reasoning and Action agent (using tool calling)" had **no tools**, while `pyproject.toml` depended on `tavily-python`. The ReAct loop had nothing to act with, and the search dependency was dead weight.
- The model string was fixed, so `.env.example` listing OpenAI, Anthropic and Fireworks keys implied a choice the code did not offer.
- `auth.py` returned `"default_user"` for every caller on a deployment whose API creates paid model runs.

## Decision

`config.py` (pydantic-settings) holds `MODEL`, `SYSTEM_PROMPT`, `TAVILY_API_KEY`, `AUTH_TOKEN` and `LANGGRAPH_URL`. `graph.build_graph()` reads them: it wires the Tavily search tool when a key is present, so the agent can actually act, and uses the configured model and prompt. The module still exposes `graph` for `langgraph.json`.

`auth.py` keeps the permissive path as the documented **development** default (a local `langgraph dev` server wants it) but enforces `Authorization: Bearer <token>`, compared in constant time, whenever `AUTH_TOKEN` is set. The authorized identity is derived from the token (never the token itself), and the shared dev identity is labelled `public`, not `default_user`.

## Consequences

`build_tools`, `build_graph`, `is_authorized` and `resolve_identity` are plain functions, unit-tested without a model or a running server. A deployment can be locked down with one environment variable, and the Tavily dependency now earns its place.
