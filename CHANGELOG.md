# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- `project/tests/conftest.py` — mocks heavy runtime dependencies (FastEmbed, Qdrant, LLM, Chainlit) so `app.py` can be imported in tests without API keys or model downloads
- `project/tests/unit/test_app.py` — 13 unit tests for `format_doc()` (8 tests) and `load_chat_model()` error paths (5 tests); 40% coverage
- `[dependency-groups] dev` in `project/pyproject.toml` — ruff, mypy, pytest, pytest-cov, pytest-asyncio
- `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.pytest.ini_options]`, `[tool.coverage.run]`, `[tool.mypy]` config sections in `project/pyproject.toml`
- `.github/workflows/ci.yml` — 3-job Python CI pipeline: `lint` (ruff check + format), `typecheck` (mypy), `test` (pytest + coverage + Codecov upload); triggers on push to `main` and PRs

### Changed
- `project/app.py` — whitespace-only reformatting applied by `ruff format` (no logic changes)
- `CONTRIBUTING.md` — development workflow, branch naming, commit conventions, PR template
- `docs/FEATURE_STATUS.md` — single source of truth for implementation status
- `docs/architecture.md` — detailed architecture, data flow, module boundaries
- `CHANGELOG.md` — this file
- `project/.env.example` — API key template (replaces accidentally committed `.env`)

### Changed
- `.gitignore` updated to explicitly ignore `.env`, `*.env`, `project/.env`

### Fixed
- Removed `GROQ_API_KEY` from git history (was committed in `project/.env` at line 2);
  key should be rotated at https://console.groq.com/keys

---

## [0.1.0] — 2026-03-09 — Initial Codebase Commit

### Summary
Initial commit of the SPARQL Query Assistant chatbot source code. This is the baseline
state of the project at the start of the development sprint.

### Added
- `project/app.py` — main application; implements:
  - `load_chat_model()` — LLM provider factory (Mistral AI + Groq)
  - `index_endpoints()` — indexes UniProt, Bgee, OMA Browser SPARQL metadata into Qdrant
  - `retrieve_docs()` — semantic similarity search (filtered by doc type)
  - `format_doc()` — formats retrieved docs as markdown for LLM context
  - `execute_query()` — extracts and executes SPARQL from LLM response
  - `on_message()` — Chainlit handler with streaming and retry loop (max 3 attempts)
  - `set_starters()` — starter question suggestions in Chainlit UI
- `project/pyproject.toml` — Python 3.12 project definition; runtime dependencies
- `project/uv.lock` — locked dependency versions
- `project/chainlit.md` — Chainlit welcome screen (default template; not yet customised)
- `project/.chainlit/config.toml` — Chainlit configuration
- `project/.chainlit/translations/` — 19 language files (Chainlit default)
- `project/data/vectordb/meta.json` — Qdrant collection metadata
- `project/data/vectordb/collection/sparql-docs/storage.sqlite` — indexed vector data
- `project/demo_embedding_search.py` — educational: demonstrates cosine similarity search
- `project/embedding_timing_demo.py` — educational: one-time vs per-query embedding timing
- `project/explore_endpoints.py` — educational: explains the three SPARQL endpoints
- `project/show_endpoint_processing.py` — educational: shows what SparqlExamplesLoader returns
- `project/step2_explanation.py` — educational: walkthrough of vector DB setup
- `.github/workflows/deploy.yml` — GitHub Actions workflow to deploy slides to GitHub Pages
- Root `README.md` — covers slides development and GitHub Pages deployment
- `LICENSE` — repository licence

### Known Issues at This Baseline
- `project/__pycache__/app.cpython-312.pyc` accidentally committed (should be in `.gitignore`)
- `project/data/vectordb/.lock` accidentally committed (runtime file; should be in `.gitignore`)
- `project/.env` accidentally committed with real API keys (keys should be rotated)
- No tests, no linter, no type checker configured
- `app.py` contains ~4 commented-out `async def main()` implementations (dead code from tutorial)
- `execute_query()` return type annotation missing `None` variant
- Demo scripts mixed with application code in `project/` (no `demos/` subfolder yet)
- `chainlit.md` shows default Chainlit boilerplate instead of project-specific content
- No CI workflow for Python code
- Only `main` branch in use; no branch protection configured

---

## Versioning Convention

| Version Segment | Meaning |
|----------------|---------|
| Major (`X.0.0`) | Breaking change to core functionality or SPARQL contract |
| Minor (`0.X.0`) | New feature (new endpoint, new provider, new module) |
| Patch (`0.0.X`) | Bug fix, refactor, docs, tooling |

---

## Course Milestone Reference

| Week | Date | Task |
|------|------|------|
| Week 10 | 02.03.26 | Codebase snapshot; start planning refactors |
| Week 11 | 09.03.26 | Git workflow established |
| Week 12 | 16.03.26 | Repository setup: README, branch protection, Issues |
| Weeks 14–15 | 30.03–06.04.26 | Refactoring; tests started; IDE tooling |
| Week 16 | 13.04.26 | Code profiling; bottleneck analysis |
| Week 17 | 20.04.26 | CI/CD setup (linter, tests, coverage) |
| Presentation | 11–18.05.26 | Final presentations and submission |
