#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/edit_section.py - Tool: edit one section of existing Uzbek wikitext.

Extracts a named section, applies a natural-language instruction via the
EDIT-role LLM, and returns a unified diff plus the path to the full edited text.
Does NOT publish — that is a separate, human-confirmed step (Phase C).
"""

from pathlib import Path

import mwparserfromhell

from core.editor import WikiEditor
from utils.diff import short_stat, unified_diff
from utils.file_handler import FileHandler
from utils.logger import logger

SCHEMA = {
    "type": "function",
    "function": {
        "name": "edit_section",
        "description": (
            "Mavjud oʻzbekcha wikitext'ning bitta boʻlimini koʻrsatma asosida tahrirlaydi "
            "(masalan 'Tarixi' boʻlimini qisqartir, manba qoʻsh va h.k.). "
            "Oʻzgarishlarni diff sifatida qaytaradi va toʻliq natijani faylga saqlaydi. "
            "Nashr qilmaydi."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "wikitext": {
                    "type": "string",
                    "description": "Toʻliq oʻzbekcha maqola wikitext'i.",
                },
                "section": {
                    "type": "string",
                    "description": (
                        "Tahrirlanadigan boʻlim sarlavhasi (masalan 'Tarixi'). "
                        "Kirish (lead) uchun 'lead' yoki 'kirish' deb yozing."
                    ),
                },
                "instruction": {
                    "type": "string",
                    "description": "Nima oʻzgartirish kerakligi haqida koʻrsatma.",
                },
            },
            "required": ["wikitext", "section", "instruction"],
        },
    },
}

_LEAD_ALIASES = {"lead", "kirish", "muqaddima", ""}


def _find_section(wikicode, section_name: str):
    """Return the Wikicode section matching section_name, or None."""
    target = section_name.strip().lower()
    sections = wikicode.get_sections(include_lead=True, flat=True)
    for sec in sections:
        headings = sec.filter_headings()
        if not headings:  # lead section
            if target in _LEAD_ALIASES:
                return sec
            continue
        title = headings[0].title.strip_code().strip().lower()
        if title == target:
            return sec
    return None


def _available_headings(wikicode) -> str:
    titles = [h.title.strip_code().strip() for h in wikicode.filter_headings()]
    return ", ".join(titles) if titles else "(boʻlim yoʻq)"


def run(wikitext: str, section: str, instruction: str) -> str:
    logger.info(f"🔧 edit_section(section={section!r})")
    if not wikitext.strip():
        return "XATO: 'wikitext' boʻsh."

    wikicode = mwparserfromhell.parse(wikitext)
    sec = _find_section(wikicode, section)
    if sec is None:
        return (
            f"XATO: '{section}' boʻlimi topilmadi. "
            f"Mavjud boʻlimlar: {_available_headings(wikicode)}"
        )

    old_section = str(sec)
    editor = WikiEditor()
    new_section = editor.edit(old_section, instruction)
    if not new_section:
        return "XATO: tahrir muvaffaq boʻlmadi."

    if new_section.strip() == old_section.strip():
        return "OK: model hech qanday oʻzgarish kiritmadi (matn oʻzgarmadi)."

    new_full = wikitext.replace(old_section, new_section, 1)

    temp_dir = Path("temp_wiki")
    temp_dir.mkdir(exist_ok=True)
    out_path = temp_dir / "edited.txt"
    FileHandler.write_file(str(out_path), new_full)

    diff = unified_diff(old_section, new_section, label=section.strip() or "lead")
    stat = short_stat(old_section, new_section)
    if len(diff) > 2000:
        diff = diff[:2000] + "\n… (diff qisqartirildi)"

    return (
        f"OK: '{section}' boʻlimi tahrirlandi ({stat}).\n"
        f"Toʻliq natija fayli: {out_path}\n"
        f"--- DIFF ---\n{diff}"
    )
