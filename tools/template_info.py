#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/template_info.py - Tool: verify a template and list its parameters.

Confirms a template exists on uz.wiki (resolving redirects) and returns its
TemplateData parameters (required/suggested first) so the agent fills it
correctly instead of guessing parameter names.
"""

from utils.logger import logger
from utils.wiki_api import check_titles, get_templatedata

SCHEMA = {
    "type": "function",
    "function": {
        "name": "template_info",
        "description": (
            "Andoza uz.wiki'da mavjudligini tasdiqlaydi va parametrlarini (TemplateData) "
            "qaytaradi. Andozani ishlatishdan oldin chaqiring — parametr nomlarini oʻylab topmang."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Andoza nomi ('Andoza:' prefiksisiz ham boʻladi), masalan 'Veb manbasi'.",
                },
            },
            "required": ["name"],
        },
    },
}


def _label(meta: dict) -> str:
    label = meta.get("label")
    if isinstance(label, dict):
        return label.get("uz") or label.get("en") or ""
    return label or ""


def _desc(meta: dict) -> str:
    d = meta.get("description")
    if isinstance(d, dict):
        return d.get("uz") or d.get("en") or ""
    return d or ""


def run(name: str) -> str:
    logger.info(f"🔧 template_info(name={name!r})")
    raw = name.strip()
    title = raw if ":" in raw else f"Andoza:{raw}"

    try:
        existence = check_titles([title])
    except Exception as e:
        return f"XATO: tekshirishda xato: {e}"

    info = existence.get(title, {})
    if not info.get("exists"):
        return (
            f"XATO: {title} mavjud EMAS. Andozani ishlatmang. "
            f"`find_template` bilan to'g'ri nomni qidiring."
        )

    redirect_note = ""
    if info.get("redirect_to"):
        redirect_note = f" (→ {info['redirect_to']} ga yoʻnaltiradi)"

    try:
        td = get_templatedata(title)
    except Exception as e:
        return f"OK: {title} mavjud{redirect_note}, lekin parametrlarni olishda xato: {e}"

    usable = title.split(":", 1)[-1]
    header = f"OK: {{{{{usable}}}}} mavjud{redirect_note}."

    if not td or not td.get("params"):
        return (
            f"{header}\nTemplateData yoʻq — parametr nomlari nomaʼlum. "
            f"Bu andozani ehtiyotkorlik bilan, faqat aniq bilgan parametrlaringiz bilan ishlating."
        )

    params = td["params"]
    required, suggested, other = [], [], []
    for pname, meta in params.items():
        entry = pname
        lbl = _label(meta)
        ds = _desc(meta)
        if lbl or ds:
            entry += f" — {lbl}{(': ' + ds) if ds else ''}".strip()
        if meta.get("required"):
            required.append(entry)
        elif meta.get("suggested"):
            suggested.append(entry)
        else:
            other.append(pname)

    lines = [header]
    if required:
        lines.append("Majburiy: " + "; ".join(required))
    if suggested:
        lines.append("Tavsiya etilgan: " + "; ".join(suggested))
    if other:
        shown = ", ".join(other[:25])
        more = f" (+{len(other) - 25} ta)" if len(other) > 25 else ""
        lines.append("Boshqa parametrlar: " + shown + more)
    return "\n".join(lines)
