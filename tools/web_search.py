#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/web_search.py - Tool: web search for sourcing new articles.

Returns ranked results (title, url, snippet) via DuckDuckGo (no API key needed).
The agent uses these as citable sources when drafting a new article.
"""

from utils.logger import logger

try:  # library renamed: ddgs (new) <- duckduckgo_search (old)
    from ddgs import DDGS
except ImportError:  # pragma: no cover
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Internetdan manba qidiradi (DuckDuckGo). Yangi maqola yozish yoki "
            "faktlarni tekshirish uchun manbalar (sarlavha, URL, qisqacha) qaytaradi."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Qidiruv soʻrovi.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Natijalar soni (standart 5, maksimal 10).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


def run(query: str, max_results: int = 5) -> str:
    logger.info(f"🔧 web_search(query={query!r}, max_results={max_results})")
    if DDGS is None:
        return "XATO: 'ddgs' kutubxonasi oʻrnatilmagan. `pipenv install ddgs` qiling."

    max_results = max(1, min(int(max_results), 10))
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"XATO: qidiruvda xato: {e}"

    if not results:
        return f"Natija topilmadi: {query!r}"

    lines = [f"'{query}' boʻyicha {len(results)} natija:"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "(sarlavhasiz)")
        url = r.get("href") or r.get("url", "")
        body = (r.get("body") or "").strip()
        if len(body) > 250:
            body = body[:250] + "…"
        lines.append(f"{i}. {title}\n   {url}\n   {body}")
    return "\n".join(lines)
