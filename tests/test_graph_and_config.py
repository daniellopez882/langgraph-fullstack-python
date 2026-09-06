"""
Graph construction and configuration.

The old graph hardcoded the model and passed ``tools=[]`` while the project
depended on tavily-python — a "tool-calling agent" with nothing to call.
"""

from __future__ import annotations

import importlib

import pytest

from react_agent.config import DEFAULT_MODEL, Settings
from react_agent.graph import build_graph, build_tools

# react_agent/__init__.py re-exports `graph` (the compiled graph), which shadows
# the submodule attribute, so `import react_agent.graph as m` would bind the
# compiled graph, not the module. import_module returns the real module.
graph_module = importlib.import_module("react_agent.graph")


class TestConfig:
    def build(self, **kw):
        return Settings(_env_file=None, **kw)

    def test_defaults(self):
        s = self.build()
        assert s.MODEL == DEFAULT_MODEL
        assert s.tools_enabled is False
        assert s.auth_required is False

    def test_a_tavily_key_enables_tools(self):
        assert self.build(TAVILY_API_KEY="tvly-x").tools_enabled is True

    def test_an_auth_token_requires_auth(self):
        assert self.build(AUTH_TOKEN="t").auth_required is True

    def test_the_model_is_configurable(self):
        assert self.build(MODEL="openai:gpt-4o").MODEL == "openai:gpt-4o"


class TestBuildTools:
    def test_no_key_means_no_tools(self, monkeypatch):
        monkeypatch.setattr(graph_module.settings, "TAVILY_API_KEY", "")
        assert build_tools() == []

    def test_a_key_wires_the_search_tool(self, monkeypatch):
        monkeypatch.setattr(graph_module.settings, "TAVILY_API_KEY", "tvly-test")
        monkeypatch.setattr(graph_module.settings, "TAVILY_MAX_RESULTS", 5)
        captured = {}

        class FakeTool:
            def __init__(self, max_results):
                captured["max_results"] = max_results

        import langchain_community.tools.tavily_search as tav

        monkeypatch.setattr(tav, "TavilySearchResults", FakeTool)
        tools = build_tools()
        assert len(tools) == 1
        assert captured["max_results"] == 5


class TestBuildGraph:
    def test_it_passes_the_configured_model_prompt_and_tools(self, monkeypatch):
        captured = {}

        def fake_create(model, tools, prompt):
            captured.update(model=model, tools=tools, prompt=prompt)
            return "compiled-graph"

        monkeypatch.setattr(graph_module, "create_react_agent", fake_create)
        monkeypatch.setattr(graph_module.settings, "MODEL", "openai:gpt-4o")
        monkeypatch.setattr(graph_module.settings, "SYSTEM_PROMPT", "be helpful")
        result = build_graph(tools=[])
        assert result == "compiled-graph"
        assert captured["model"] == "openai:gpt-4o"
        assert captured["prompt"] == "be helpful"
        assert captured["tools"] == []

    def test_tools_default_to_the_configured_set(self, monkeypatch):
        captured = {}

        def fake_create(model, tools, prompt):
            captured["tools"] = tools
            return "g"

        monkeypatch.setattr(graph_module, "create_react_agent", fake_create)
        monkeypatch.setattr(graph_module, "build_tools", lambda: ["a-tool"])
        build_graph()
        assert captured["tools"] == ["a-tool"]

    def test_the_module_exposes_a_compiled_graph(self):
        assert graph_module.graph is not None


class TestNoHardcodedModelOutsideConfig:
    def test_the_retired_style_literal_is_not_hardcoded_in_graph(self):
        import inspect

        source = inspect.getsource(graph_module.build_graph)
        assert "claude-3-5-haiku" not in source  # comes from settings.MODEL now


@pytest.mark.parametrize("value", [None, ""])
def test_empty_authorization_types(value):
    """resolve_identity tolerates missing headers."""
    from react_agent.auth import resolve_identity

    assert isinstance(resolve_identity(value), str)
