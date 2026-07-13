# wiki-agent — "Wikipedia uchun Claude Code"

Oʻzbekcha Vikipediya uchun **agentik** yordamchi. Foydalanuvchi tabiiy tilda buyruq
beradi, agent esa vositalar (tools) yordamida vazifani bajaradi: maqolani tarjima
qilish, Vikipediyadan matn olish va h.k. Yozuvchi amallar (nashr) **inson tasdigʻi**
bilan bajariladi.

> Bu loyiha mavjud `wikipedia-translator` pipeline'idan ilhomlangan, lekin uni **agentic
> tool-use** arxitekturasiga aylantiradi va **ko'p provayderli** abstraktsiya qo'shadi.

## Arxitektura

```
cli.py ──► agent/loop.py  (LLM ↔ tool dispatch)
                │
                ├── tools/translate_full_article  ──► core/pipeline.py  (5-bosqichli, deterministik)
                ├── tools/fetch_article
                └── ... (web_search, edit_section, publish — keyingi bosqichlar)
                │
           providers/  (OpenAI; keyin Anthropic/DeepSeek/Mistral/Qwen)
```

- **Gibrid**: toʻliq tarjima — bitta deterministik vosita; ochiq vazifalar — agentik loop.
- **Rol bo'yicha provayder**: `config.py` da agent / tarjima / review uchun alohida
  provayder+model tanlash mumkin (`AGENT_PROVIDER`, `TRANSLATION_PROVIDER`, ...).

## Ishga tushirish

```bash
cp .env.example .env        # OPENAI_API_KEY ni kiriting
PIPENV_IGNORE_VIRTUALENVS=1 pipenv install

# Interaktiv chat
PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python cli.py

# Bir martalik buyruq
PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python cli.py "Avicenna maqolasini oʻzbekchaga tarjima qil"
```

Tarjima natijasi `temp_wiki/<Maqola nomi>.txt` ga saqlanadi.

## Holat (roadmap)

- [x] **A (MVP)**: provayder abstraktsiyasi, agentik loop, `fetch_article`, `translate_full_article`.
- [x] **B**: `web_search` (yangi maqola), `edit_section` (tahrirlash).
- [ ] **C**: `publish` — inson tasdigʻi bilan uz.wiki'ga nashr (pywikibot).
- [ ] **D**: Chrome toolbar kengaytmasi (xuddi shu agent yadrosi).
