#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
providers/__init__.py - Provider factory.

`get_provider(name)` returns an LLMProvider instance. Only "openai" is wired up
in the MVP; the registry is the single place to add future providers
(anthropic, deepseek, mistral, qwen, ...).
"""

from functools import lru_cache

import config
from providers.base import LLMProvider
from providers.openai_provider import OpenAIProvider


@lru_cache(maxsize=None)
def get_provider(name: str) -> LLMProvider:
    """Return a cached provider instance by name."""
    name = (name or "openai").lower()
    if name == "openai":
        return OpenAIProvider(api_key=config.OPENAI_API_KEY)
    raise ValueError(
        f"Noma'lum provayder: '{name}'. Hozircha faqat 'openai' qo'llab-quvvatlanadi."
    )
