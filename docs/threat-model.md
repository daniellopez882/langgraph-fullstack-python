# Threat model

Scope: a single LangGraph deployment that serves a ReAct agent, a permissive
auth hook, and a FastHTML chat UI, all wired by `langgraph.json`. It is a
starter/demo derived from the LangGraph react-agent template and the
AnswerDotAI SSE chatbot example.

## What it holds

| Asset | Where | Why it matters |
|---|---|---|
| Model provider keys | `.env` (`ANTHROPIC_/OPENAI_/FIREWORKS_API_KEY`) | Billable; each run spends them |
| `TAVILY_API_KEY` | `.env` | Billable search |
| `AUTH_TOKEN` | `.env` | Gates the deployment API when set |
| Conversation threads | LangGraph checkpoint store | Whatever users type |

`.env` is gitignored; CI fails if it is tracked and scans history with gitleaks.

## Threats

### T1 — Open, paid deployment *(was open)*

The auth hook returned `"default_user"` for every caller; anyone reaching the
deployment could create runs and spend model credit. **Controls.** With
`AUTH_TOKEN` set, a bearer token is required and checked in constant time; the
permissive path is the documented dev-only default. **Residual.** The UI in
front is still a public demo; put the deployment behind the token (and a
network boundary) before exposing it.

### T2 — XSS via streamed model output *(was open)*

Model content was swapped into the DOM as `innerHTML` unescaped. **Controls.**
Every chunk is `escape_html`-ed before framing; a `<script>` payload becomes
inert text. See [ADR 0002](adr/0002-sse-framing-and-escaping.md).

### T3 — Prompt injection through tools

With Tavily enabled, the agent reads web search results — attacker-controllable
text — and may act on them. **Controls.** The only tool is read-only search;
output is escaped before display. **Residual.** A search result can still
steer the model's answer; there is no output review.

### T4 — Thread enumeration

The UI namespaces threads by a client-set `user_id` cookie, which is
spoofable. For a demo this is acceptable; a real deployment should derive the
thread owner from the authenticated identity (`resolve_identity`), not a
cookie.

### T5 — Supply chain

`pip-audit`, `bandit` and gitleaks run in CI; `mypy --strict` and `ruff` gate
the code.

## Not addressed

- The FastHTML UI has no auth of its own; it is a demo front end.
- No rate limit or per-caller quota.
- Thread ownership is cookie-based in the UI (see T4).
