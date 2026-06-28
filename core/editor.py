#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/editor.py - LLM-based wikitext editor (provider-agnostic).

Applies a natural-language instruction to a chunk of Uzbek wikitext using the
EDIT-role provider, preserving wikitext structure.
"""

from typing import Optional

import config
from providers import get_provider
from utils.logger import logger


class WikiEditor:
    """Edit a section of wikitext according to a user instruction."""

    def __init__(self):
        self.provider = get_provider(config.EDIT_PROVIDER)
        self.model = config.EDIT_MODEL

    def edit(self, text: str, instruction: str) -> Optional[str]:
        """Return the edited wikitext, or None on failure."""
        system_prompt = config.EDIT_SYSTEM_PROMPT
        user_prompt = config.EDIT_USER_PROMPT.format(instruction=instruction, text=text)

        try:
            response = self.provider.complete(
                messages=[{"role": "user", "content": user_prompt}],
                model=self.model,
                system=system_prompt,
            )
            edited = (response.content or "").strip()
            if edited.startswith("```"):
                edited = edited.split("\n", 1)[-1]
            if edited.endswith("```"):
                edited = edited.rsplit("\n", 1)[0]
            return edited.strip()
        except Exception as e:
            logger.fail(f"Tahrir xatosi: {e}")
            return None
