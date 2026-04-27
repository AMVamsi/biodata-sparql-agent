# Feature Status — biodata-sparql-agent

> **Single source of truth for implementation status.**
> Read this file before assuming something is missing or needs to be built.
> Update this file every time a task is completed.

---

## How to Read This Table

| Status | Meaning |
|--------|---------|
| `implemented` | Fully working; do not rebuild |
| `baseline` | First working version; may be refined only if explicitly instructed |
| `planned` | Not started; do not build unless the current task explicitly requests it |
| `todo` | Accepted for near-term work; not yet started |
| `in_progress` | Actively being built — check branch before touching |
| `blocked` | Waiting on an external decision or dependency |
| `deprecated` | Do not use for new work |

---

## Application Core

| Feature | Status | Notes | Implemented In |
|---------|--------|-------|----------------|
| `load_chat_model()` | `implemented` | Provider/model string split; Mistral + Groq backends | `llm.py` |
| `index_endpoints()` | `implemented` | UniProt, Bgee, OMA; deletes + recreates collection on each call | `retrieval.py` |
| `retrieve_docs()` | `implemented` | Filters by `doc_type`: query examples + schema shapes; top-3 each | `retrieval.py` |
| `format_doc()` | `implemented` | Pure function; markdown codeblock with `#+ endpoint:` comment | `retrieval.py` |
| `execute_query()` | `implemented` | Extracts SPARQL from LLM markdown; calls live SPARQL endpoint; returns `list \| None` | `sparql.py` |
| Retry loop (max 3 attempts) | `implemented` | Appends corrective feedback on no-results; re-calls LLM | `app.py` |
| `on_message()` Chainlit handler | `implemented` | Streaming responses; step display for retrieved docs + results | `app.py` |
| `set_starters()` | `implemented` | Rat orthologs starter question | `app.py` |
| LLM provider: Mistral AI | `implemented` | `mistralai/mistral-small-latest` (active) | `app.py` |
| LLM provider: Groq | `implemented` | Commented out by default; toggle by changing `load_chat_model` call | `app.py` |
| Constants + SYSTEM_PROMPT | `implemented` | Extracted to `config.py`; SYSTEM_PROMPT locked | `config.py` |
| Code modularisation | `implemented` | `app.py` split into `config`, `llm`, `retrieval`, `sparql` — clean modules | all |
| mypy zero-error pass | `implemented` | All type errors resolved across 5 modules | all |

---

## Project Structure

| Feature | Status | Notes |
|---------|--------|-------|
| Demo scripts in `demos/` subfolder | `planned` | Currently 5 scripts mixed with app code in `project/` |
| `project/README.md` for chatbot | `todo` | Current README only covers slides, not chatbot setup |
| `chainlit.md` customised | `todo` | Still shows default Chainlit boilerplate text |
| `tests/` folder created | `implemented` | `project/tests/conftest.py` + `tests/unit/test_app.py`; 13 tests |
| `docs/` folder created | `implemented` | Contains `FEATURE_STATUS.md` and `architecture.md` |

---

## Configuration and Tooling

| Feature | Status | Notes |
|---------|--------|-------|
| `ruff` linter + formatter | `implemented` | Configured in `pyproject.toml`; zero errors across all modules |
| `mypy` type checker | `implemented` | Configured in `pyproject.toml`; `ignore_missing_imports = true`; 0 errors |
| `pytest` + `pytest-cov` | `implemented` | Configured in `pyproject.toml`; 13 tests, 69% coverage |
| `pytest-asyncio` | `implemented` | `asyncio_mode = auto`; ready for async Chainlit tests |
| Dev dependency group in `pyproject.toml` | `implemented` | `[dependency-groups] dev` with ruff, mypy, pytest, pytest-cov, pytest-asyncio |
| `__pycache__/` in `.gitignore` | `todo` | Bytecode already committed; need to untrack + add to `.gitignore` |
| `.mypy_cache/` in `.gitignore` | `todo` | Present locally; should be explicitly ignored |
| `data/vectordb/.lock` in `.gitignore` | `todo` | Runtime lock file currently tracked in git |
| Remove tracked `__pycache__/*.pyc` | `todo` | `git rm --cached` needed |
| Remove tracked `data/vectordb/.lock` | `todo` | `git rm --cached` needed |

---

## CI/CD (GitHub Actions)

| Feature | Status | Notes |
|---------|--------|-------|
| Slides deploy to GitHub Pages | `implemented` | `.github/workflows/deploy.yml`; triggers on push to `main` |
| Python CI workflow (`ci.yml`) | `implemented` | 3 jobs: lint (ruff), typecheck (mypy), test+coverage (pytest) — Week 17 |
| Ruff check in CI | `implemented` | `lint` job; runs on push to `main` and on PRs |
| Test run on PR + merge | `implemented` | `test` job; coverage XML uploaded to Codecov |
| Coverage upload (Codecov) | `implemented` | `codecov/codecov-action@v5`; requires `CODECOV_TOKEN` secret |
| Mypy check in CI | `implemented` | `typecheck` job in `ci.yml` |
| `pytest` in CI | `implemented` | `test` job in `ci.yml` |
| Coverage upload to Codecov | `implemented` | `codecov/codecov-action@v5`; requires `CODECOV_TOKEN` secret |
| Branch protection on `main` | `planned` | Requires CI checks to be set up first; configure on GitHub |

---

## Tests (`tests/`)

| Test | Status | Notes |
|------|--------|-------|
| `test_format_doc` | `todo` | Pure function — easiest to write first |
| `test_load_chat_model_error` | `todo` | Test `ValueError` on unknown provider |
| `test_load_chat_model_mistral` | `todo` | Mock `ChatMistralAI`; assert return type |
| `test_load_chat_model_groq` | `todo` | Mock `ChatGroq`; assert return type |
| `test_retrieve_docs` | `todo` | Mock Qdrant client; assert filtering by `doc_type` |
| `test_execute_query_no_block` | `todo` | Input with no SPARQL block → assert `None` |
| `test_execute_query_with_block` | `todo` | Input with valid SPARQL block → assert query + endpoint extracted |
| Integration tests | `planned` | Requires live endpoints; scope for later |

---

## Profiling (Week 16 Task)

| Feature | Status | Notes |
|---------|--------|-------|
| `index_endpoints()` flamegraph | `planned` | Known slow path: network + HTTP + embedding |
| `on_message()` profiling | `planned` | Identify LLM vs embedding vs SPARQL time split |
| Bottleneck documentation | `planned` | To be written in `docs/profiling.md` |
| Query result caching | `planned` | Optional: `lru_cache` keyed on question for repeated queries |
| Incremental re-indexing | `planned` | Optional: skip deleting collection if endpoints unchanged |

---

## Future / Out of Scope

| Feature | Status | Notes |
|---------|--------|-------|
| PubMed literature extraction | `planned` | Via UniProt `rdfs:seeAlso` links or PubMed E-utilities |
| Additional SPARQL endpoints | `planned` | e.g., ChEMBL, Ensembl |
| Multi-user / production deployment | `planned` | Requires shared Qdrant + auth |
| Query result caching (persistent) | `planned` | Redis or disk-based cache |
| Custom endpoint upload via UI | `planned` | User-configurable endpoint list |

---

## Last Updated

| Date | Updated By | Change Summary |
|------|-----------|----------------|
| 2026-04-27 | contributor | Initial FEATURE_STATUS.md created from codebase analysis |
