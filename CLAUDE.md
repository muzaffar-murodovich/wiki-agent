# CLAUDE.md

Guidance for Claude Code (or any agent) working in this repository.

## What this project is

**wiki-agent** is an **agentic** assistant for Uzbek Wikipedia ("Claude Code for Wikipedia").
The user gives natural-language commands; the agent uses tools to carry them out: translate an
article, fetch wikitext from Wikipedia, search the web to draft a new article, or edit a section
of existing wikitext.

Language: **en→uz only** for now. Interface: **terminal CLI** (a Chrome toolbar extension is planned).

> Inspired by the existing `wikipedia-translator` pipeline; its proven `core/` and `utils/`
> modules were copied and adapted into this repo.

## ⛔ Hard rule: NO automated publishing

The agent must **never** write to / publish on Wikipedia. There is no `publish` tool, no pywikibot
write/login path, no "save with one command" — not even behind a y/N confirmation.

**Why:** an AI could publish without genuine review, or a human could rubber-stamp a publish
without actually reading it; articles this agent produces must be published by a **human who takes
responsibility**, not by a bot (per Wikipedia community norms). The agent is draft-only — its job
ends at producing clean wikitext. (Export/preview/handoff UX will live in the future Chrome
extension, where saving on-wiki is still a manual human action.)

## Architecture

Hybrid: an **agentic tool-use loop** at the top (the LLM decides which tool to call), but full
translation is a single **deterministic** tool (the LLM does not re-derive the pipeline each time).

```
cli.py ──► agent/loop.py  (LLM ↔ tool dispatch ↔ repeat)
                │
                ├── tools/translate_full_article ─► core/pipeline.py (5-phase, deterministic)
                ├── tools/fetch_article          ─► utils/wiki_fetcher
                ├── tools/web_search             ─► ddgs (DuckDuckGo)
                └── tools/edit_section           ─► core/editor + mwparserfromhell
                │
           providers/  (LLM abstraction: OpenAI now; future Anthropic/DeepSeek/Mistral/Qwen)
```

### Key directories
- **`providers/`** — provider-agnostic LLM layer. `base.py` (`LLMProvider` ABC, `LLMResponse`,
  `ToolCall`), `openai_provider.py`, `__init__.py` (`get_provider(name)` factory).
- **`agent/loop.py`** — the `Agent` class. Tool-use loop; write tools (`tools.WRITE_TOOLS`) ask
  `confirm()` first (none exist today). Canonical message format is the OpenAI chat format.
- **`tools/`** — each tool module exposes `SCHEMA` (OpenAI function-tool) + `run(**kwargs) -> str`.
  `__init__.py` is the registry (`SCHEMAS`, `dispatch()`, `tool_names()`).
- **`core/`** — `pipeline.py` (PREPARE→TRANSLATE→FINALIZE→LOCALIZE→REVIEW, `translate_article(raw)`),
  `translator.py`, `reviewer.py`, `editor.py` (all go through `providers/`), plus `processor.py`,
  `wikidata_fetcher.py`, `cache_manager.py` (adapted from the translator).
- **`utils/`** — `wiki_fetcher.py`, `localization.py`, `regex_patterns.py`, `file_handler.py`,
  `logger.py`, `diff.py`.
- **`config.py`** — all settings; role-based provider/model.
- **Data files:** `localization_map.json`, `translation_rules.md`.

### Role-based providers (important design)
In `config.py` the AGENT / TRANSLATION / REVIEW / EDIT roles each have a **separate** provider+model:
`AGENT_PROVIDER`, `TRANSLATION_PROVIDER`, `REVIEW_PROVIDER`, `EDIT_PROVIDER` (+ matching `_MODEL`).
Rationale: one model may be stronger at agentic reasoning while another is stronger at Uzbek
translation. MVP uses OpenAI for every role. Adding a provider = implement it in `providers/` and
add one line to the factory.

## Running

Dependencies live in a dedicated pipenv env. `.env` must contain `OPENAI_API_KEY`.

```bash
PIPENV_IGNORE_VIRTUALENVS=1 pipenv install          # first time

# Interactive chat
PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python cli.py

# One-shot command
PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python cli.py "Translate the Avicenna article into Uzbek"
```

Outputs are saved under `temp_wiki/` (translation: `<Article name>.txt`, edit: `edited.txt`).
`PYWIKIBOT_NO_USER_CONFIG=2` is set — pywikibot is used read-only (Wikidata lookups) only.

## Conventions
- User-facing text and logs are **Uzbek**; code and docstrings are English.
- To add a tool: create `tools/<name>.py` (`SCHEMA` + `run`), then add it to `_MODULES` in
  `tools/__init__.py`. If a tool mutates external state, add it to `WRITE_TOOLS` and use the
  `confirm` flow. (But writing to Wikipedia is forbidden — see the hard rule above.)
- All LLM calls go through `providers/`; do not import `openai` directly outside
  `providers/openai_provider.py`.
- Logger methods: `info/success/warning/fail/section/stats` (note `progress(current, total)` takes
  two positional args).

## Status / roadmap
- [x] **A (MVP)**: providers, agent loop, `translate_full_article`, `fetch_article`.
- [x] **B**: `web_search` (new article), `edit_section` (editing).
- [ ] **D**: Chrome toolbar extension — same agent core as backend; export/preview/handoff UX lives
      here. (The human still does the publishing.)
- ~~C (publish)~~ — **cancelled**; automated publishing is forbidden.
