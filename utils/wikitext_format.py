#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
utils/wikitext_format.py - Deterministic wikitext cleanups for drafted articles.

LLMs tend to write English-style "text.<ref>...</ref>", but uz.wiki convention
puts the punctuation AFTER the reference: "text<ref>...</ref>.". This is a purely
mechanical fix, so we do it deterministically instead of relying on the prompt.
"""

import re

# One or more consecutive <ref>...</ref> or self-closing <ref ... /> tags.
_REF_RUN = r"(?:<ref\b[^>]*?>.*?</ref>|<ref\b[^>]*?/>)+"
# A sentence punctuation char sitting immediately before a ref run.
_PUNCT_BEFORE_REF = re.compile(r"([.,;:!?])(" + _REF_RUN + r")", re.DOTALL)


def fix_ref_punctuation(text: str) -> str:
    """Move punctuation that precedes a <ref> run to after it (uz.wiki style)."""
    # Repeat until stable (handles a punct followed by ref then another punct+ref).
    prev = None
    while prev != text:
        prev = text
        text = _PUNCT_BEFORE_REF.sub(r"\2\1", text)
    return text


def cleanup_wikitext(text: str) -> str:
    """Apply all deterministic cleanups. Extend here as more rules are found."""
    return fix_ref_punctuation(text)
