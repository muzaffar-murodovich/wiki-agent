#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/pipeline.py - Deterministic full-article translation pipeline.

This is the battle-tested 5-phase pipeline from the original project, wrapped as
a single callable so the agent can invoke it as one deterministic tool instead of
re-deriving the steps each time.

    PREPARE -> TRANSLATE -> FINALIZE -> LOCALIZE -> REVIEW
"""

import os
import time
from typing import Dict, Optional

os.environ.setdefault("PYWIKIBOT_NO_USER_CONFIG", "2")

import pywikibot  # noqa: E402

pywikibot.config.maxlag = 5
pywikibot.config.put_throttle = 1
pywikibot.config.noisysleep = False
pywikibot.config.max_retries = 3
pywikibot.config.retry_wait = 10

from core.cache_manager import WikiCache  # noqa: E402
from core.processor import WikiTextProcessor  # noqa: E402
from core.reviewer import WikiReviewer  # noqa: E402
from core.translator import WikiTranslator  # noqa: E402
from core.wikidata_fetcher import WikidataFetcher  # noqa: E402
from utils.localization import LocalizationManager  # noqa: E402
from utils.logger import logger  # noqa: E402
from utils.regex_patterns import fix_arabic_transliteration  # noqa: E402


def translate_article(raw_wikitext: str) -> Dict[str, object]:
    """
    Run the full en->uz translation pipeline on English wikitext.

    Args:
        raw_wikitext: English Wikipedia wikitext.

    Returns:
        A dict with keys:
          - ok (bool)
          - text (str | None): Uzbek wikitext on success
          - error (str | None)
          - stats (dict): sizes, link/category/template counts, timings
    """
    if not raw_wikitext or not raw_wikitext.strip():
        return {"ok": False, "text": None, "error": "Bo'sh kirish matni", "stats": {}}

    start = time.time()

    cache = WikiCache()
    fetcher = WikidataFetcher(cache)
    processor = WikiTextProcessor(fetcher, cache)
    translator = WikiTranslator()
    localization = LocalizationManager()
    reviewer = WikiReviewer()

    try:
        logger.section("📝 PHASE 1: PREPARE")
        prepared_text, link_map, cat_map, tpl_map, ref_map = processor.prepare(raw_wikitext)

        logger.section("🤖 PHASE 2: TRANSLATE")
        translated_text = translator.translate(prepared_text)
        if not translated_text:
            return {"ok": False, "text": None, "error": "Tarjima muvaffaq bo'lmadi", "stats": {}}

        logger.section("🔧 PHASE 3: FINALIZE")
        finalized_text = processor.finalize(translated_text, ref_map)

        logger.section("🌐 PHASE 4: LOCALIZE")
        result = localization.apply(finalized_text)
        result = fix_arabic_transliteration(result)

        logger.section("🔍 PHASE 5: REVIEW")
        if reviewer.is_available():
            reviewed = reviewer.review(result)
            if reviewed:
                result = reviewed
            else:
                logger.warning("Review muvaffaq bo'lmadi — Phase 4 natijasi saqlanadi")
        else:
            logger.warning("Review o'tkazib yuborildi (qoidalar fayli topilmadi)")
    except Exception as e:
        logger.fail(f"Pipeline xatosi: {e}")
        return {"ok": False, "text": None, "error": str(e), "stats": {}}

    elapsed = time.time() - start
    stats = {
        "input_size": len(raw_wikitext),
        "output_size": len(result),
        "links": len(link_map),
        "categories": len(cat_map),
        "templates": len(tpl_map),
        "seconds": round(elapsed, 2),
    }
    return {"ok": True, "text": result, "error": None, "stats": stats}
