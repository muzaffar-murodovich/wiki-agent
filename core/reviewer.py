#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/reviewer.py - Post-translation review (provider-agnostic).

Applies translation_rules.md to localized wikitext via the REVIEW-role provider.
"""

from pathlib import Path
from typing import Optional

import config
from providers import get_provider
from utils.logger import logger


class WikiReviewer:
    """Review and fix translated wikitext according to translation_rules.md."""

    RULES_FILE = Path("translation_rules.md")

    def __init__(self):
        self.provider = get_provider(config.REVIEW_PROVIDER)
        self.model = config.REVIEW_MODEL
        self.rules = self._load_rules()
        self.stats = {"reviews": 0, "tokens_used": 0, "cached_tokens": 0, "prompt_tokens": 0}

        if self.rules:
            logger.success(f"Tahrir qoidalari yuklandi ({len(self.rules)} belgi)")
        else:
            logger.warning("translation_rules.md topilmadi — review o'tkazib yuboriladi")

    def _load_rules(self) -> Optional[str]:
        if not self.RULES_FILE.exists():
            return None
        try:
            return self.RULES_FILE.read_text(encoding="utf-8")
        except Exception as e:
            logger.fail(f"Qoidalar faylini o'qishda xato: {e}")
            return None

    def is_available(self) -> bool:
        return self.rules is not None

    def review(self, text: str) -> Optional[str]:
        """Review and fix localized wikitext using translation_rules.md."""
        if not self.is_available():
            return text

        system_prompt = config.REVIEW_SYSTEM_PROMPT.format(rules=self.rules)
        user_prompt = config.REVIEW_USER_PROMPT.format(text=text)

        try:
            response = self.provider.complete(
                messages=[{"role": "user", "content": user_prompt}],
                model=self.model,
                system=system_prompt,
            )
            reviewed = (response.content or "").strip()
            if reviewed.startswith("```"):
                reviewed = reviewed.split("\n", 1)[-1]
            if reviewed.endswith("```"):
                reviewed = reviewed.rsplit("\n", 1)[0]
            reviewed = reviewed.strip()

            self.stats["reviews"] += 1
            self._record_usage(response.usage)
            logger.success(f"Tahrir tugadi ({len(reviewed)} belgi)")
            return reviewed
        except Exception as e:
            logger.fail(f"Tahrir xatosi: {e}")
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
            "Tahrir Statistikasi",
            model=self.model,
            reviews=self.stats["reviews"],
            tokens_used=self.stats["tokens_used"],
            cached_tokens=f"{self.stats['cached_tokens']}/{self.stats['prompt_tokens']} ({hit_rate:.1f}%)",
        )
