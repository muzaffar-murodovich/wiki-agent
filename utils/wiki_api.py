#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
utils/wiki_api.py - Thin helpers over the target-language Wikipedia API.

Used by the live template/category tools (find_template, template_info,
check_exists) so the agent can verify and discover templates/categories instead
of inventing names. Host is derived from config.TARGET_LANG.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

import config

_API = f"https://{config.TARGET_LANG}.wikipedia.org/w/api.php"
_UA = "wiki-agent/0.1 (Uzbek Wikipedia assistant)"

# Namespace numbers
NS_TEMPLATE = 10
NS_CATEGORY = 14


def _api_get(params: Dict[str, str]) -> dict:
    params = {**params, "format": "json", "formatversion": "2"}
    url = _API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_pages(query: str, namespace: int, limit: int = 8) -> List[Dict[str, str]]:
    """Full-text search within a namespace. Returns [{title, snippet}]."""
    data = _api_get({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": str(namespace),
        "srlimit": str(limit),
        "srprop": "snippet",
    })
    out = []
    for r in data.get("query", {}).get("search", []):
        snippet = r.get("snippet", "")
        # strip HTML tags from snippet
        snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "")
        out.append({"title": r.get("title", ""), "snippet": snippet})
    return out


def check_titles(titles: List[str]) -> Dict[str, Dict]:
    """
    Check existence of titles (any namespace). Resolves redirects.

    Returns {title: {"exists": bool, "redirect_to": str|None}}.
    """
    if not titles:
        return {}
    data = _api_get({
        "action": "query",
        "titles": "|".join(titles),
        "redirects": "1",
        "prop": "info",
    })
    q = data.get("query", {})
    redirects = {r["from"]: r["to"] for r in q.get("redirects", [])}
    norm = {n["from"]: n["to"] for n in q.get("normalized", [])}

    resolved = {p["title"]: (not p.get("missing", False)) for p in q.get("pages", [])}

    result: Dict[str, Dict] = {}
    for title in titles:
        t = norm.get(title, title)
        redirect_to = redirects.get(t)
        final = redirect_to or t
        result[title] = {
            "exists": resolved.get(final, False),
            "redirect_to": redirect_to,
        }
    return result


def get_templatedata(template_title: str) -> Optional[dict]:
    """
    Return TemplateData for a template (params/description), or None if absent.
    `template_title` may be with or without the 'Andoza:' prefix.
    """
    if ":" not in template_title:
        template_title = f"Andoza:{template_title}"
    data = _api_get({
        "action": "templatedata",
        "titles": template_title,
        "redirects": "1",
        "includeMissingTitles": "1",
    })
    pages = data.get("pages", {})
    if not pages:
        return None
    page = list(pages.values())[0]
    if "params" not in page and "notemplatedata" not in page:
        return None
    return page
