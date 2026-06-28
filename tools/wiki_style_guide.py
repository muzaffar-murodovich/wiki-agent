#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/wiki_style_guide.py - Tool: return the uz.wiki authoring guide.

Grounds the agent in verified uz.wiki conventions (article skeleton, <ref>
mechanics, citation/templates, categories) before it writes a new article, so it
doesn't invent template names. The guide lives in references/uz_wiki_guide.md.
"""

from pathlib import Path

from utils.logger import logger

_GUIDE_PATH = Path("references/uz_wiki_guide.md")

SCHEMA = {
    "type": "function",
    "function": {
        "name": "wiki_style_guide",
        "description": (
            "Oʻzbek Vikipediyasi yozuv qoʻllanmasini qaytaradi: maqola tuzilishi, <ref> "
            "mexanikasi, tasdiqlangan andoza/iqtibos nomlari, turkumlar. Yangi maqola "
            "yozishdan OLDIN shu vositani chaqiring."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


def run() -> str:
    logger.info("🔧 wiki_style_guide()")
    if not _GUIDE_PATH.exists():
        return f"XATO: qoʻllanma topilmadi: {_GUIDE_PATH}"
    return _GUIDE_PATH.read_text(encoding="utf-8")
