#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/check_exists.py - Tool: verify that uz.wiki pages exist.

Checks templates (Andoza:...), categories (Turkum:...), or article titles before
the agent references them — so it never adds a nonexistent category or links a
missing page. Resolves redirects.
"""

from utils.logger import logger
from utils.wiki_api import check_titles

SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_exists",
        "description": (
            "uz.wiki'da sahifa(lar) mavjudligini tekshiradi — turkum ([[Turkum:...]]), "
            "andoza (Andoza:...) yoki maqola nomlari. Yangi maqolaga turkum yoki havola "
            "qoʻshishdan oldin tekshiring; mavjud boʻlmaganini qoʻshmang."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "titles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Tekshiriladigan toʻliq nomlar roʻyxati, masalan "
                        "['Turkum:Oʻzbekiston daryolari', 'Toshkent']."
                    ),
                },
            },
            "required": ["titles"],
        },
    },
}


def run(titles: list) -> str:
    logger.info(f"🔧 check_exists({len(titles)} ta nom)")
    if not titles:
        return "XATO: 'titles' boʻsh."
    # Cap to keep the API request reasonable.
    titles = [str(t).strip() for t in titles if str(t).strip()][:50]

    try:
        results = check_titles(titles)
    except Exception as e:
        return f"XATO: tekshirishda xato: {e}"

    lines = []
    for title in titles:
        info = results.get(title, {"exists": False, "redirect_to": None})
        if info["exists"]:
            mark = "✓ MAVJUD"
            if info.get("redirect_to"):
                mark += f" (→ {info['redirect_to']})"
        else:
            mark = "✗ YOʻQ — ishlatmang"
        lines.append(f"{mark}: {title}")
    return "\n".join(lines)
