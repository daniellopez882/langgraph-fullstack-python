# ADR 0002 — SSE is framed per line, and model output is escaped before the DOM

**Status:** accepted

## Context

The streaming route did, for each chunk:

```python
yield f"event: message\ndata: {content}\n\n"
```

Two defects in one line:

1. **Framing.** Server-Sent Events require every line of a multi-line payload
   to carry its own `data:` field. A model reply containing a newline produced
   a frame whose second line had no `data:` prefix; the browser's EventSource
   dropped or mis-parsed it, so multi-line answers rendered wrong.
2. **Escaping.** The content was streamed to the page and swapped into the DOM
   as `innerHTML`. A model reply — or a tool result the model quotes back —
   containing `<script>` or `<img onerror=…>` executed in the visitor's
   browser. The transcript is not trusted output.

## Decision

`sse.format_sse(data, event)` emits one `data:` field per line (handling `\n`
and `\r\n`) and terminates with a blank line. `sse.escape_html` escapes the
five significant characters. The streaming route escapes each chunk, then
frames it: `format_sse(escape_html(content), event="message")`.

Both are pure functions with unit tests, including a multi-line payload and a
`<script>`/`<img onerror>` payload that must not survive.

## Consequences

Multi-line replies render correctly, and a hostile or prompt-injected model
reply is inert HTML text in the page rather than executable markup. The UI's
own note ("unauthenticated demo — do not share private data") stays, because
this ADR hardens the transport, not the trust model of a public demo.
