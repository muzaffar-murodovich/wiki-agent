#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
utils/diff.py - Unified diff helper for previewing edits.

Used by edit tools (and later publish) to show the user what will change
before anything is written.
"""

import difflib


def unified_diff(old: str, new: str, label: str = "matn") -> str:
    """Return a unified diff string between old and new text."""
    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        fromfile=f"{label} (eski)",
        tofile=f"{label} (yangi)",
        lineterm="",
    )
    text = "\n".join(diff)
    return text or "(o'zgarish yo'q)"


def short_stat(old: str, new: str) -> str:
    """Return a compact +added/-removed line summary."""
    sm = difflib.SequenceMatcher(a=old.splitlines(), b=new.splitlines())
    added = removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
    return f"+{added} / -{removed} qator"
