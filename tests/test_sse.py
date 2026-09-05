"""
SSE framing and escaping.

The old streaming line was `f"event: message\\ndata: {content}\\n\\n"`: a
multi-line reply broke the framing, and the content reached the DOM as
innerHTML unescaped.
"""

from __future__ import annotations

from react_agent.sse import escape_html, format_sse


class TestFraming:
    def test_a_single_line(self):
        assert format_sse("hello", event="message") == "event: message\ndata: hello\n\n"

    def test_a_multi_line_payload_gets_a_data_field_per_line(self):
        out = format_sse("line one\nline two\nline three", event="message")
        assert (
            out
            == "event: message\ndata: line one\ndata: line two\ndata: line three\n\n"
        )

    def test_crlf_is_handled(self):
        out = format_sse("a\r\nb", event="message")
        assert out == "event: message\ndata: a\ndata: b\n\n"

    def test_an_empty_payload_still_frames(self):
        assert format_sse("", event="close") == "event: close\ndata: \n\n"

    def test_no_event_line_when_event_is_none(self):
        assert format_sse("hi") == "data: hi\n\n"

    def test_every_event_ends_with_a_blank_line(self):
        assert format_sse("x\ny", event="message").endswith("\n\n")


class TestEscape:
    def test_the_five_significant_characters(self):
        assert escape_html("<b>\"'&") == "&lt;b&gt;&quot;&#39;&amp;"

    def test_a_script_tag_cannot_survive(self):
        assert "<script>" not in escape_html("<script>alert(1)</script>")

    def test_plain_text_is_unchanged(self):
        assert escape_html("hello world 123") == "hello world 123"

    def test_streaming_escapes_before_framing(self):
        """A model reply with HTML is escaped, then framed."""
        out = format_sse(escape_html("<img src=x onerror=alert(1)>"), event="message")
        assert "<img" not in out
        assert "&lt;img" in out
