"""Boot regression for the FastHTML app module.

`app.py` imported ``picolink`` from ``fasthtml.common``. That convenience
export was removed after fasthtml 0.12, and the dependency was pinned only
with a lower bound (``>=0.12.1``), so a fresh install resolved 0.14.x and the
LangGraph server died at startup with::

    ImportError: cannot import name 'picolink' from 'fasthtml.common'

No test imported the module, so nothing caught it until the container was
booted. This one does: it fails on the old import and passes once the Pico
stylesheet link is defined locally.
"""

from __future__ import annotations

import importlib

from fasthtml.common import Link


def test_app_module_imports_and_exposes_app() -> None:
    module = importlib.import_module("react_agent.app")
    assert hasattr(module, "app"), "app.py must expose `app` for langgraph.json"


def test_pico_stylesheet_is_a_local_link_not_a_fasthtml_export() -> None:
    module = importlib.import_module("react_agent.app")
    pico = module.picolink
    assert isinstance(pico, type(Link()))
    href = pico.attrs.get("href", "")
    assert "picocss/pico" in href
    # Pinned CDN version, not `@latest`.
    assert "@latest" not in href
