#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/translator.py - Translation engine (provider-agnostic).

Wraps an LLMProvider for the TRANSLATION role. Identical behaviour to the
original, but the vendor is selected via config.TRANSLATION_PROVIDER/MODEL.
"""

from typing import Optional

import config
from providers import get_provider
from utils.logger import logger


class WikiTranslator:
    """Translate Wikipedia articles to Uzbek via the configured provider."""

    def __init__(self):
        self.provider = get_provider(config.TRANSLATION_PROVIDER)
        self.model = config.TRANSLATION_MODEL
        self.stats = {"translations": 0, "tokens_used": 0, "cached_tokens": 0, "prompt_tokens": 0}
        logger.info(f"🤖 Tarjima provayderi: {self.provider.name} ({self.model})")

    def translate(self, prepared_text: str) -> Optional[str]:
        """Translate prepared (placeholder-laden) wikitext to Uzbek."""
        user_prompt = config.TRANSLATION_USER_PROMPT.format(text=prepared_text)

        try:
            response = self.provider.complete(
                messages=[{"role": "user", "content": user_prompt}],
                model=self.model,
                system=config.TRANSLATION_SYSTEM_PROMPT,
            )
            translated = response.content
            self.stats["translations"] += 1
            self._record_usage(response.usage)
            logger.success(f"Tarjima tugadi ({len(translated or '')} belgi)")
            return translated
        except Exception as e:
            logger.fail(f"Tarjima xatosi: {e}")
            return None

    def _record_usage(self, usage: dict):
        if not usage:
            return
        self.stats["tokens_used"] += usage.get("total_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        cached = usage.get("cached_tokens", 0)
        self.stats["prompt_tokens"] += prompt_tokens
        self.stats["cached_tokens"] += cached
        hit_rate = (cached / prompt_tokens * 100) if prompt_tokens else 0
        logger.info(f"Cache: {cached}/{prompt_tokens} token ({hit_rate:.1f}%)")

    def print_stats(self):
        hit_rate = (
            self.stats["cached_tokens"] / self.stats["prompt_tokens"] * 100
            if self.stats["prompt_tokens"] else 0
        )
        logger.stats(
            "Tarjima Statistikasi",
            model=self.model,
            translations=self.stats["translations"],
            tokens_used=self.stats["tokens_used"],
            cached_tokens=f"{self.stats['cached_tokens']}/{self.stats['prompt_tokens']} ({hit_rate:.1f}%)",
        )
