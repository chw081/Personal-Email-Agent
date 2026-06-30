"""Extract readable text and attachment metadata from Gmail MIME payloads."""

from __future__ import annotations

import base64
import re
from html import unescape


def decode_body_data(data: str) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def html_to_text(html: str) -> str:
    if not html.strip():
        return ""

    without_scripts = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    with_breaks = re.sub(r"(?i)<br\s*/?>", "\n", without_scripts)
    with_breaks = re.sub(r"(?i)</p>", "\n\n", with_breaks)
    with_breaks = re.sub(r"(?i)</div>", "\n", with_breaks)
    without_tags = re.sub(r"<[^>]+>", " ", with_breaks)
    text = unescape(without_tags)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _header_value(headers: list[dict[str, str]], name: str) -> str:
    target = name.lower()
    for header in headers:
        if header.get("name", "").lower() == target:
            return header.get("value", "")
    return ""


def _part_has_attachment(part: dict) -> bool:
    if part.get("filename"):
        return True
    disposition = _header_value(part.get("headers", []), "Content-Disposition").lower()
    return "attachment" in disposition


def extract_message_content(payload: dict) -> tuple[str, bool]:
    """Return extracted plain-text body and whether the message has attachments."""
    plain_parts: list[str] = []
    html_parts: list[str] = []
    has_attachment = False

    def walk(part: dict) -> None:
        nonlocal has_attachment

        if _part_has_attachment(part):
            has_attachment = True

        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data", "")

        if mime_type == "text/plain" and data:
            plain_parts.append(decode_body_data(data))
        elif mime_type == "text/html" and data:
            html_parts.append(decode_body_data(data))

        for subpart in part.get("parts", []) or []:
            walk(subpart)

    if payload:
        walk(payload)

    if plain_parts:
        body_text = "\n\n".join(part.strip() for part in plain_parts if part.strip())
        return body_text, has_attachment

    if html_parts:
        body_text = html_to_text("\n\n".join(html_parts))
        return body_text, has_attachment

    return "", has_attachment
