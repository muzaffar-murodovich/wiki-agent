#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/fetch_article.py - Tool: fetch wikitext from Wikipedia.
"""

from utils.logger import logger
from utils.wiki_fetcher import fetch_wikitext, is_redirect

SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_article",
        "description": (
            "Vikipediyadan maqolaning xom wikitext'ini yuklab oladi. "
            "Maqola nomi yoki Vikipediya URL'i orqali ishlaydi."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Maqola nomi (masalan 'Avicenna') yoki Vikipediya URL'i.",
                },
                "lang": {
                    "type": "string",
                    "description": "Til kodi (masalan 'en' yoki 'uz'). Standart: 'en'.",
                    "default": "en",
                },
            },
            "required": ["title"],
        },
    },
}


def run(title: str, lang: str = "en") -> str:
    logger.info(f"🔧 fetch_article(title={title!r}, lang={lang!r})")
    wikitext, resolved = fetch_wikitext(title, lang)
    if not wikitext:
        return f"XATO: '{title}' ({lang}.wikipedia) topilmadi yoki yuklab bo'lmadi."

    redirect = is_redirect(wikitext)
    note = f" (redirect → {redirect})" if redirect else ""
    preview = wikitext[:500]
    return (
        f"OK: '{resolved}' yuklandi{note}. Hajmi: {len(wikitext)} belgi.\n"
        f"--- Boshlanishi ---\n{preview}\n--- (qisqartirildi) ---"
    )
