#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
config.py - Central configuration for wiki-agent.

Inherits the proven translation settings from the original wikipedia-translator
and adds a role-based provider layer: the AGENT and the TRANSLATION/REVIEW roles
can each point at a different provider+model. MVP uses OpenAI for every role.
"""

import os
from pathlib import Path

# --- Provider keys ---

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Role-based provider/model selection ---
# Future-proofing: the agent (reasoning/tool-use) and the translation/review
# roles can use different providers. Empirically Anthropic is stronger for agentic
# reasoning while OpenAI is stronger for Uzbek translation — this split lets us mix
# them later without touching call sites. MVP keeps every role on OpenAI.

AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "openai")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-5.2")

TRANSLATION_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "openai")
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "gpt-5.2")

REVIEW_PROVIDER = os.getenv("REVIEW_PROVIDER", "openai")
REVIEW_MODEL = os.getenv("REVIEW_MODEL", "gpt-5.4-mini")

# Backwards-compatible alias used by a few copied modules.
OPENAI_MODEL = TRANSLATION_MODEL

# --- Wikipedia Settings ---

WIKIPEDIA_FAMILY = "wikipedia"
SOURCE_LANG = "en"  # Source language
TARGET_LANG = "uz"  # Target language

# --- Parallel Processing Settings ---

MAX_WORKERS = 1
REQUEST_DELAY = 1

# --- Pywikibot Configuration ---

PYWIKIBOT_CONFIG = {
    "maxlag": 10,
    "put_throttle": 1,
    "noisysleep": False,
    "max_retries": 8,
    "retry_wait": 20,
}

# --- Localization Settings ---

LOCALIZATION_FILE = Path("localization_map.json")

# --- Reference Compression ---

REF_COMPRESS_THRESHOLD = 20

# --- Fallback Mappings ---

FALLBACK_TEMPLATE_MAP_EN2UZ = {
    "infobox person": "Shaxs bilgiqutisi",
    "infobox place": "Joyni bilgiqutisi",
    "infobox country": "Davlatni bilgiqutisi",
}

FALLBACK_CATEGORY_PREFIX = "Turkum"

# --- Logging Settings ---

LOG_LEVEL = "INFO"

# --- Agent Settings ---

AGENT_MAX_ITERATIONS = 12  # safety cap on tool-use loop iterations per user turn

AGENT_SYSTEM_PROMPT = """Siz oʻzbekcha Vikipediya uchun yordamchi agentsiz ("Wikipedia uchun Claude Code").

Foydalanuvchi tabiiy tilda buyruq beradi. Siz quyidagi vositalardan (tools) foydalanib vazifani bajarasiz:
- to'liq maqolani inglizchadan oʻzbekchaga tarjima qilish,
- Vikipediyadan wikitext olish,
- internetdan manba qidirish,
- mavjud matnni tahrirlash,
- oʻzgarishlarni koʻrsatish (diff) va inson tasdigʻi bilan nashr qilish.

QOIDALAR:
1) Toʻliq maqola tarjimasi soʻralsa — albatta `translate_full_article` vositasini chaqiring. Tarjimani oʻzingiz qoʻlda yozmang.
2) Vositadan kelgan natijaga ishoning; uni qayta yozib chiqmang.
3) Nashr (`publish`) yoki yozuvchi amallar inson tasdigʻini talab qiladi — buni tizim oʻzi soʻraydi.
4) Foydalanuvchiga oʻzbek tilida, qisqa va aniq javob bering.
5) Vazifa tugagach, qisqacha xulosa qiling (nima qilindi, natija qayerda)."""

# --- Translation Prompt Settings ---

TRANSLATION_SYSTEM_PROMPT = "Siz oʻzbekcha Vikipediya muharririsiz."

TRANSLATION_USER_PROMPT = """
Quyidagi wikitext'ni oʻzbek tiliga tarjima qiling. MUHIM QOIDALAR:

1) Quyidagi placeholder'larni aynan oʻz holicha qoldiring:
   - [[Q12345|...]] koʻrinishidagi havolalarda: QID (masalan, Q12345) oʻzgarmasin; faqat '|' dan keyingi label'ni oʻzbekchaga tarjima qiling.
   - ⟦CAT:Q12345|...⟧ koʻrinishidagi tokenlarda: QID oʻzgarmasin; faqat '|' dan keyingi label'ni oʻzbekchaga tarjima qiling.
   - Template nomlari 'TPL:Q12345' koʻrinishida boʻladi — ularni aynan shunday qoldiring. Template parametrlarining qiymatlari tarjima qiling, lekin parametr kalitlari (key) oʻzgartirmang.
   - REF_ bilan boshlanadigan qisqa manbalarni oʻzgartirmang.

2) Oddiy ingliz wikilinklarini (QID emas) toʻliq tarjima qiling — HAM target, HAM label. Masalan:
   - [[Treaty of Safar]] → [[Safar shartnomasi]]
   - [[Tarsus, Mersin|Tarsus]] → [[Tarsus, Mersin|Tars]]
   - [[Sa'd al-Dawla al-Qawwasi|Sa'd al-Dawla]] → [[Saʼd ad-Davla al-Qavvasiy|Saʼd ad-Davla]]
   - Agar oʻzbek tilidagi nomi nomaʼlum boʻlsa — fonetik transliteratsiya qiling.
   - [[Rashiq al-Nasimi]] → [[Roshiq an-Nasimiy]] (arab ismlarini oʻzbek imlosiga moslashtiring)
   - [[Traditionalist theology (Islam)|Athari]] → [[Anʼanaviy ilohiyot (Islom)|asariy]] (qavs ichidagi disambiguation'ni ham tarjima qiling)

3) Strukturani saqlang: sarlavhalar, roʻyxatlar, {{...}} va boshqa wikitext sintaksisi buzilmasin.

4) Izoh yozmang. Faqat wikitext chiqaring.

Matn:
```{text}```
"""

# --- Review Prompt Settings ---

REVIEW_SYSTEM_PROMPT = """Siz oʻzbekcha Vikipediya muharririsiz.

Sizning vazifangiz — berilgan oʻzbekcha wikitext'ni quyidagi qoidalar asosida tekshirish va tuzatish.

QOIDALAR:
{rules}

---

MUHIM CHEKLOVLAR:
1) Faqat qoidalarda koʻrsatilgan xatolarni tuzating. Boshqa hech narsani oʻzgartirmang.
2) Wikitext tuzilishini ({{...}}, [[...]], <ref>...</ref> va boshqalar) buzmang.
3) Izoh yozmang. Faqat tuzatilgan wikitext chiqaring."""

REVIEW_USER_PROMPT = """MATN:
```
{text}
```
"""

# --- Error Messages ---

ERROR_MESSAGES = {
    "maxlag_timeout": "⚠️  Wikipedia serverlari band. Keyinroq urinib ko'ring.",
    "api_error": "❌ API xatosi. Internet ulanishini tekshiring.",
    "invalid_qid": "⚠️  Noto'g'ri QID formatı.",
    "file_not_found": "❌ Fayl topilmadi.",
    "json_error": "❌ JSON formatida xato.",
}

# --- Additional Settings ---

VERBOSE = True
DEBUG = False
