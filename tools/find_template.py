#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/find_template.py - Tool: discover uz.wiki templates by keyword.

Searches the Template (Andoza:) namespace so the agent can find a real template
(e.g. an infobox) instead of guessing its name. Pair with `template_info` to get
the template's parameters before using it.
"""

from utils.logger import logger
from utils.wiki_api import NS_TEMPLATE, search_pages

SCHEMA = {
    "type": "function",
    "function": {
        "name": "find_template",
        "description": (
            "uz.wiki'dan kalit soʻz boʻyicha andoza (Andoza:) qidiradi — masalan infobox "
            "kerak boʻlganda. Mavjud andoza nomlarini qaytaradi. Topgach, parametrlarini "
            "bilish uchun `template_info` ni chaqiring. Andoza nomini oʻzingiz oʻylab topmang."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Kalit soʻz, masalan 'daryo', 'shaxs', 'shahar maʼlumotnoma'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Natijalar soni (standart 8).",
                    "default": 8,
                },
            },
            "required": ["query"],
        },
    },
}


def run(query: str, limit: int = 8) -> str:
    logger.info(f"🔧 find_template(query={query!r})")
    limit = max(1, min(int(limit), 15))
    try:
        results = search_pages(query, NS_TEMPLATE, limit)
    except Exception as e:
        return f"XATO: qidiruvda xato: {e}"

    if not results:
        return f"'{query}' boʻyicha andoza topilmadi. Boshqa kalit soʻz bilan urinib koʻring."

    lines = [f"'{query}' boʻyicha {len(results)} andoza:"]
    for i, r in enumerate(results, 1):
        # Title like "Andoza:Veb manbasi" → usable as {{Veb manbasi}}
        name = r["title"].split(":", 1)[-1]
        snippet = r["snippet"].strip()
        extra = f" — {snippet}" if snippet else ""
        lines.append(f"{i}. {{{{{name}}}}}  ({r['title']}){extra}")
    lines.append("\nParametrlarini bilish uchun `template_info` ni chaqiring.")
    return "\n".join(lines)
