"""Unit tests for project/app.py.

Coverage targets (pure / easily-isolated functions):
  - format_doc()        — pure function, most testable
  - load_chat_model()   — error path (unknown provider raises ValueError)

Heavy dependencies (LLM, FastEmbed, Qdrant, Chainlit, sparql-llm) are mocked
in tests/conftest.py so that app.py can be imported without API keys or
model downloads.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Make sure the project directory is on the path so `import app` works from
# any working directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import app  # noqa: E402


# ── helpers ────────────────────────────────────────────────────────────────


def _make_doc(payload: dict) -> MagicMock:
    """Return a minimal mock of qdrant ScoredPoint with the given payload."""
    doc = MagicMock()
    doc.payload = payload
    return doc


# ── format_doc ─────────────────────────────────────────────────────────────


class TestFormatDoc:
    """Tests for format_doc(), which formats a retrieved document into a
    markdown snippet consumed by the SYSTEM_PROMPT."""

    def test_query_example_includes_endpoint_comment(self):
        """SPARQL query examples must embed the '#+ endpoint:' comment."""
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints query examples",
                "question": "What are the rat orthologs of human TP53?",
                "answer": "SELECT ?ortholog WHERE { ... }",
                "endpoint_url": "https://sparql.omabrowser.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        assert "#+ endpoint: https://sparql.omabrowser.org/sparql/" in result

    def test_query_example_uses_sparql_language_tag(self):
        """Code-block language tag must be 'sparql' for query examples."""
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints query examples",
                "question": "Sample question",
                "answer": "SELECT * WHERE { ?s ?p ?o }",
                "endpoint_url": "https://sparql.uniprot.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        assert "```sparql" in result

    def test_schema_doc_has_no_endpoint_comment(self):
        """Class-schema documents must not inject an '#+ endpoint:' comment."""
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints classes schema",
                "question": "What classes exist?",
                "answer": "up:Protein a owl:Class .",
                "endpoint_url": "https://sparql.uniprot.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        assert "#+ endpoint:" not in result

    def test_schema_doc_has_empty_language_tag(self):
        """Schema documents get an empty language tag (plain code block)."""
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints classes schema",
                "question": "What classes exist?",
                "answer": "up:Protein a owl:Class .",
                "endpoint_url": "https://sparql.uniprot.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        # The code block should open with triple backticks immediately followed
        # by a newline (empty language tag), not ```sparql.
        assert "```\n" in result

    def test_output_contains_question_text(self):
        """The formatted string must include the original question."""
        question = "Which genes are expressed in the mouse brain?"
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints query examples",
                "question": question,
                "answer": "SELECT ?gene WHERE { ... }",
                "endpoint_url": "https://www.bgee.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        assert question in result

    def test_output_contains_answer_text(self):
        """The formatted string must include the SPARQL answer."""
        answer = "SELECT ?gene WHERE { ?gene a up:Gene . }"
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints query examples",
                "question": "Find all genes",
                "answer": answer,
                "endpoint_url": "https://sparql.uniprot.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        assert answer in result

    def test_missing_endpoint_url_shows_not_provided(self):
        """When endpoint_url is absent, the comment must say 'not provided'."""
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints query examples",
                "question": "Any question",
                "answer": "SELECT * WHERE {}",
            }
        )
        result = app.format_doc(doc)
        assert "#+ endpoint: not provided" in result

    def test_output_ends_with_double_newline(self):
        """Formatted docs should end with a double newline for clean joining."""
        doc = _make_doc(
            {
                "doc_type": "SPARQL endpoints query examples",
                "question": "Q",
                "answer": "A",
                "endpoint_url": "https://sparql.uniprot.org/sparql/",
            }
        )
        result = app.format_doc(doc)
        assert result.endswith("\n\n")


# ── load_chat_model ────────────────────────────────────────────────────────


class TestLoadChatModel:
    """Tests for load_chat_model(), focusing on the error-path that requires
    no real API keys or network access."""

    def test_unknown_provider_raises_value_error(self):
        """An unrecognised provider prefix must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown provider: ollama"):
            app.load_chat_model("ollama/llama3")

    def test_unknown_provider_message_contains_provider_name(self):
        """The error message must name the bad provider."""
        with pytest.raises(ValueError) as exc_info:
            app.load_chat_model("anthropic/claude-3-5-sonnet")
        assert "anthropic" in str(exc_info.value)

    def test_model_string_without_slash_raises(self):
        """A model string with no '/' separator must raise (split fails)."""
        with pytest.raises((ValueError, AttributeError)):
            app.load_chat_model("mistral-small-latest")

    def test_mistral_provider_accepted(self):
        """'mistralai' prefix must be accepted without raising."""
        # The factory calls ChatMistralAI(...) which is mocked in conftest,
        # so no real API call is made.
        result = app.load_chat_model("mistralai/mistral-small-latest")
        assert result is not None

    def test_groq_provider_accepted(self):
        """'groq' prefix must be accepted without raising."""
        result = app.load_chat_model("groq/llama-3.1-8b-instant")
        assert result is not None
