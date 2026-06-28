#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tools/__init__.py - Tool registry.

Aggregates every agent-facing tool. Each tool module exposes:
  - SCHEMA: an OpenAI function-tool schema dict
  - run(**kwargs) -> str

`SCHEMAS` is the list passed to the provider; `dispatch(name, args)` executes a
tool by name and always returns a string result for the model.
"""

from typing import Any, Dict

from tools import edit_section, fetch_article, translate_full_article, web_search

# Order matters only for display; the model picks by name.
_MODULES = [
    translate_full_article,
    fetch_article,
    web_search,
    edit_section,
]

SCHEMAS = [m.SCHEMA for m in _MODULES]
_REGISTRY = {m.SCHEMA["function"]["name"]: m.run for m in _MODULES}

# Tools that modify external state and require human confirmation before running.
WRITE_TOOLS = {"publish", "apply_edit"}


def tool_names() -> list:
    return list(_REGISTRY.keys())


def dispatch(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool by name with the given arguments dict."""
    func = _REGISTRY.get(name)
    if func is None:
        return f"XATO: noma'lum vosita '{name}'."
    try:
        return func(**arguments)
    except TypeError as e:
        return f"XATO: '{name}' uchun noto'g'ri argumentlar: {e}"
    except Exception as e:
        return f"XATO: '{name}' bajarilishida xato: {e}"
