"""
Patch heavy runtime dependencies so the application modules can be imported
without API keys, model downloads, or a running Qdrant instance.

All patches are applied to sys.modules before any test file imports the
application modules, which means they intercept the module-level
instantiation of:
  - TextEmbedding (FastEmbed) — would download the BAAI model
  - QdrantClient              — would open the on-disk vector DB
  - ChatMistralAI             — would require MISTRAL_API_KEY
"""

import sys
from unittest.mock import MagicMock

# ── mock sub-modules that app.py imports at the top level ──────────────────
_MOCK_MODULES = [
    "fastembed",
    "qdrant_client",
    "qdrant_client.http",
    "qdrant_client.http.models",
    "qdrant_client.models",
    "langchain_mistralai",
    "langchain_groq",
    "langchain_ollama",
    "chainlit",
    "sparql_llm",
    "sparql_llm.validate_sparql",
    "sparql_llm.utils",
]

for _mod in _MOCK_MODULES:
    sys.modules.setdefault(_mod, MagicMock())
