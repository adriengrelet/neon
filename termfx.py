#!/usr/bin/env python3
import os
import re
import sys

ANSI_COLORS = {
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
}
ANSI_RESET = "\x1b[0m"
CHOICE_PREFIX_RE = re.compile(r"^(\s*)([A-Za-z0-9]+[.)])(\s+)(.*)$")


def supports_ansi(stream=None):
    stream = stream or sys.stdout

    if os.environ.get("NO_COLOR"):
        return False

    force_color = os.environ.get("FORCE_COLOR", "").strip().lower()
    if force_color in ("1", "true", "yes", "on"):
        return True

    if not hasattr(stream, "isatty") or not stream.isatty():
        return False

    term = os.environ.get("TERM", "").strip().lower()
    if term in ("", "dumb"):
        return False

    return True


def color(text, color_name, enabled=None):
    text = str(text)
    if enabled is None:
        enabled = supports_ansi()
    if not enabled:
        return text

    ansi = ANSI_COLORS.get(color_name)
    if not ansi:
        return text

    return f"{ansi}{text}{ANSI_RESET}"


def color_choice_line(text, marker_color="yellow", text_color="blue", enabled=None):
    text = str(text)
    match = CHOICE_PREFIX_RE.match(text)
    if not match:
        return color(text, text_color, enabled=enabled)

    leading, marker, spacing, label = match.groups()
    return (
        f"{leading}"
        f"{color(marker, marker_color, enabled=enabled)}"
        f"{spacing}"
        f"{color(label, text_color, enabled=enabled)}"
    )


def normalize_ansi_escapes(text):
    if not isinstance(text, str) or not text:
        return ""

    # Convert escaped forms from JSON strings into real ESC codes.
    return (
        text.replace("\\u001b", "\x1b")
        .replace("\\033", "\x1b")
        .replace("\\x1b", "\x1b")
    )
