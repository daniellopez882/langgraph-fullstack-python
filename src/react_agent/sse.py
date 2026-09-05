r"""Server-Sent Events framing and HTML escaping.

The streaming path in app.py did:

    yield f"event: message\\ndata: {content}\\n\\n"

Two defects in that one line. First, SSE requires every line of a multi-line
payload to carry its own ``data:`` prefix; a model reply containing a newline
produced a frame whose second line was not `data:` and was dropped or
misparsed by the browser's EventSource. Second, the content was streamed into
the page and swapped into the DOM as innerHTML with no escaping, so a model
reply (or a tool result the model quotes) containing ``<script>`` ran in the
visitor's browser.

These are pure functions so they can be tested without a running server.
"""

from __future__ import annotations

_ESCAPES = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
}


def escape_html(text: str) -> str:
    """Escape the five HTML-significant characters."""
    return "".join(_ESCAPES.get(char, char) for char in text)


def format_sse(data: str, event: str | None = None) -> str:
    """One correctly framed SSE message.

    Every line of ``data`` gets its own ``data:`` field, so a multi-line
    payload survives. A trailing blank line terminates the event.
    """
    lines = []
    if event is not None:
        lines.append(f"event: {event}")
    # Split on \n and \r\n; each line becomes its own data field. An empty
    # payload still emits one `data:` so the event is well-formed.
    for line in data.split("\n") if data else [""]:
        lines.append(f"data: {line.rstrip(chr(13))}")
    return "\n".join(lines) + "\n\n"
