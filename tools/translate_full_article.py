#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/translate_full_article.py - Tool: full en->uz article translation.

The ONE deterministic high-level tool. Wraps core.pipeline.translate_article so
the agent calls it instead of re-deriving the translation steps. Accepts either
an English article title (fetched automatically) or raw wikitext, runs the proven
pipeline, saves the Uzbek result to temp_wiki/, and returns a short report.
"""

import re
from pathlib import Path

from core.pipeline import translate_article
from utils.file_handler import FileHandler
from utils.logger import logger
from utils.wiki_fetcher import fetch_wikitext

SCHEMA = {
    "type": "function",
    "function": {
        "name": "translate_full_article",
        "description": (
            "Inglizcha Vikipediya maqolasini TO'LIQ oʻzbekchaga tarjima qiladi "
            "(wikilink, template, kategoriya va manbalarni saqlagan holda). "
            "Maqola nomi berilsa, avtomatik yuklab oladi. Natijani faylga saqlaydi. "
            "Toʻliq tarjima soʻralganda ALBATTA shu vositadan foydalaning."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Inglizcha maqola nomi (masalan 'Avicenna'). wikitext berilmasa shart.",
                },
                "wikitext": {
                    "type": "string",
                    "description": "Xom inglizcha wikitext (ixtiyoriy). Berilsa, title yuklanmaydi.",
                },
            },
            "required": [],
        },
    },
}


def _safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip() or "article"


def run(title: str = "", wikitext: str = "") -> str:
    logger.info(f"🔧 translate_full_article(title={title!r}, wikitext={'<berildi>' if wikitext else 'yoʻq'})")

    raw = wikitext
    resolved_title = title
    if not raw:
        if not title:
            return "XATO: 'title' yoki 'wikitext' dan biri kerak."
        raw, resolved_title = fetch_wikitext(title, "en")
        if not raw:
            return f"XATO: '{title}' inglizcha Vikipediyadan topilmadi."

    result = translate_article(raw)
    if not result["ok"]:
        return f"XATO: tarjima muvaffaq bo'lmadi — {result['error']}"

    uz_text = result["text"]
    stats = result["stats"]

    # Save output to temp_wiki/
    temp_dir = Path("temp_wiki")
    temp_dir.mkdir(exist_ok=True)
    name = resolved_title or title
    # Prefer the bold article name inside the wikitext if present.
    bold = re.search(r"'''(.+?)'''", uz_text)
    if bold:
        name = bold.group(1).strip()
    out_path = temp_dir / f"{_safe_filename(name)}.txt"
    FileHandler.write_file(str(out_path), uz_text)

    preview = uz_text[:600]
    return (
        f"OK: tarjima tugadi.\n"
        f"Fayl: {out_path}\n"
        f"Hajm: {stats['input_size']} → {stats['output_size']} belgi | "
        f"havola: {stats['links']}, kategoriya: {stats['categories']}, "
        f"template: {stats['templates']} | vaqt: {stats['seconds']}s\n"
        f"--- Natija boshlanishi ---\n{preview}\n--- (qisqartirildi) ---"
    )
