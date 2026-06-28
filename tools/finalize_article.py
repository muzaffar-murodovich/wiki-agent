#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/finalize_article.py - Tool: deterministic cleanup + save of a drafted article.

The agent drafts a new article, then passes it here. This applies mechanical
uz.wiki fixups the LLM is unreliable at (e.g. moving punctuation after <ref>),
saves the result to temp_wiki/, and returns the cleaned wikitext to present.
"""

import re
from pathlib import Path

from utils.file_handler import FileHandler
from utils.logger import logger
from utils.wikitext_format import cleanup_wikitext

SCHEMA = {
    "type": "function",
    "function": {
        "name": "finalize_article",
        "description": (
            "Yangi yozilgan maqola wikitext'ini uz.wiki uslubiga deterministik moslaydi "
            "(masalan tinish belgisini <ref> dan keyinga oʻtkazadi) va faylga saqlaydi. "
            "Yangi maqola tayyor boʻlgach, ALBATTA shu vositani chaqiring va uning natijasini "
            "foydalanuvchiga koʻrsating."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "wikitext": {"type": "string", "description": "Maqolaning toʻliq wikitext'i."},
                "title": {"type": "string", "description": "Maqola nomi (fayl nomi uchun)."},
            },
            "required": ["wikitext"],
        },
    },
}


def _safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip() or "article"


def run(wikitext: str, title: str = "") -> str:
    logger.info(f"🔧 finalize_article(title={title!r})")
    if not wikitext.strip():
        return "XATO: 'wikitext' boʻsh."

    cleaned = cleanup_wikitext(wikitext)

    name = title
    if not name:
        bold = re.search(r"'''(.+?)'''", cleaned)
        name = bold.group(1).strip() if bold else "maqola"

    temp_dir = Path("temp_wiki")
    temp_dir.mkdir(exist_ok=True)
    out_path = temp_dir / f"{_safe_filename(name)}.txt"
    FileHandler.write_file(str(out_path), cleaned)

    changed = "Ha" if cleaned != wikitext else "Yoʻq (oʻzgarish kerak boʻlmadi)"
    return (
        f"OK: maqola tayyor.\n"
        f"Deterministik tuzatish kiritildimi: {changed}\n"
        f"Fayl: {out_path}\n"
        f"--- TOZALANGAN WIKITEXT ---\n{cleaned}"
    )
