#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/cite_source.py - Tool: build a correct uz.wiki <ref> citation.

Deterministic: the LLM provides the source fields, this tool produces the exact
`<ref>{{<Template>|...}}</ref>` string using template names verified against
uz.wikipedia.org. The model must NOT hand-write citation templates.
"""

from utils.logger import logger

# Verified against uz.wikipedia.org API (2026-06-28). Keys are the agent-facing types.
_TEMPLATES = {
    "web": "Veb manbasi",
    "book": "Kitob manbasi",
    "news": "Yangiliklar manbasi",
    "journal": "Cite journal",
}

SCHEMA = {
    "type": "function",
    "function": {
        "name": "cite_source",
        "description": (
            "Oʻzbek Vikipediyasi uchun toʻgʻri <ref> iqtibosini yaratadi (tasdiqlangan "
            "andoza nomlari bilan). Manba qoʻshganda iqtibos andozasini QOʻLDA yozmang — "
            "shu vositani chaqiring va natijani matnga joylang."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": list(_TEMPLATES.keys()),
                    "description": "Manba turi: web, book, news, journal.",
                },
                "title": {"type": "string", "description": "Sarlavha (majburiy)."},
                "url": {"type": "string", "description": "URL (veb/yangilik uchun)."},
                "author": {"type": "string", "description": "Muallif(lar) toʻliq ismi."},
                "work": {
                    "type": "string",
                    "description": "Sayt/nashr/jurnal nomi (website/work/journal).",
                },
                "publisher": {"type": "string", "description": "Nashriyot/tashkilot."},
                "date": {"type": "string", "description": "Manba sanasi (YYYY-MM-DD yoki yil)."},
                "access_date": {"type": "string", "description": "Qaralgan sana (veb uchun)."},
                "language": {"type": "string", "description": "Til kodi, masalan 'en' (oʻzbekcha boʻlsa shart emas)."},
                "isbn": {"type": "string", "description": "ISBN (kitob uchun)."},
                "pages": {"type": "string", "description": "Sahifa(lar)."},
                "name": {
                    "type": "string",
                    "description": "Nomli manba uchun ref nomi (takror ishlatish uchun, ixtiyoriy).",
                },
            },
            "required": ["type", "title"],
        },
    },
}


def run(type: str, title: str, url: str = "", author: str = "", work: str = "",
        publisher: str = "", date: str = "", access_date: str = "", language: str = "",
        isbn: str = "", pages: str = "", name: str = "") -> str:
    logger.info(f"🔧 cite_source(type={type!r}, title={title!r})")
    template = _TEMPLATES.get(type)
    if not template:
        return f"XATO: noma'lum manba turi '{type}'. Ruxsat: {', '.join(_TEMPLATES)}."

    # 'work' maps to |journal= for journals, |work= otherwise.
    work_param = "journal" if type == "journal" else "work"

    fields = [
        ("title", title),
        ("url", url),
        ("author", author),
        (work_param, work),
        ("publisher", publisher),
        ("date", date),
        ("access-date", access_date),
        ("language", language),
        ("isbn", isbn),
        ("pages", pages),
    ]
    parts = [f"{k}={v.strip()}" for k, v in fields if v and v.strip()]
    citation = "{{" + template + " |" + " |".join(parts) + "}}"

    if name.strip():
        ref = f'<ref name="{name.strip()}">{citation}</ref>'
        reuse = f'<ref name="{name.strip()}" />'
        return f"{ref}\n(Takror ishlatish uchun: {reuse})"
    return f"<ref>{citation}</ref>"
