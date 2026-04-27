"""Vector database setup, document indexing, retrieval, and formatting."""

from __future__ import annotations

import logging

from fastembed import TextEmbedding
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import FieldCondition, Filter, MatchValue, ScoredPoint
from sparql_llm import SparqlExamplesLoader, SparqlInfoLoader, SparqlVoidShapesLoader

from config import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL_NAME,
    ENDPOINTS,
    RETRIEVED_DOCS_COUNT,
)

embedding_model = TextEmbedding(EMBEDDING_MODEL_NAME)
vectordb = QdrantClient(path="data/vectordb")


def index_endpoints() -> None:
    """Index SPARQL endpoint metadata into the local vector database.

    Loads query examples, schema shapes, and endpoint descriptions for every
    URL listed in ``ENDPOINTS``, then deletes and recreates the Qdrant
    collection so the index is always up to date.

    Side effect: rewrites ``data/vectordb/`` on disk.
    """
    docs: list[Document] = []
    for endpoint in ENDPOINTS:
        logging.info(f"🔎 Retrieving metadata for {endpoint['endpoint_url']}")
        docs += SparqlExamplesLoader(
            endpoint["endpoint_url"],
            examples_file=endpoint.get("examples_file"),
        ).load()
        docs += SparqlVoidShapesLoader(
            endpoint["endpoint_url"],
            void_file=endpoint.get("void_file"),
            examples_file=endpoint.get("examples_file"),
        ).load()
    docs += SparqlInfoLoader(ENDPOINTS, source_iri="https://www.expasy.org/").load()  # type: ignore[arg-type]

    if vectordb.collection_exists(COLLECTION_NAME):
        vectordb.delete_collection(COLLECTION_NAME)
    vectordb.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSIONS, distance=Distance.COSINE
        ),
    )
    embeddings = embedding_model.embed([q.page_content for q in docs])
    vectordb.upload_collection(
        collection_name=COLLECTION_NAME,
        vectors=[embed.tolist() for embed in embeddings],
        payload=[doc.metadata for doc in docs],
    )
    logging.info(f"✅ Indexed {len(docs)} documents in collection {COLLECTION_NAME}")


def retrieve_docs(question: str) -> list[ScoredPoint]:
    """Retrieve the most relevant documents for a natural-language question.

    Runs two filtered Qdrant queries — one for SPARQL query examples and one
    for class-schema shapes — and returns up to ``RETRIEVED_DOCS_COUNT``
    results for each type.

    Args:
        question: The user's natural-language question.

    Returns:
        A combined list of scored Qdrant points.
    """
    question_embeddings = next(iter(embedding_model.embed([question])))
    retrieved = vectordb.query_points(
        collection_name=COLLECTION_NAME,
        query=question_embeddings,
        limit=RETRIEVED_DOCS_COUNT,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="doc_type",
                    match=MatchValue(value="SPARQL endpoints query examples"),
                )
            ]
        ),
    ).points
    retrieved += vectordb.query_points(
        collection_name=COLLECTION_NAME,
        query=question_embeddings,
        limit=RETRIEVED_DOCS_COUNT,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="doc_type",
                    match=MatchValue(value="SPARQL endpoints classes schema"),
                )
            ]
        ),
    ).points
    return retrieved


def format_doc(doc: ScoredPoint) -> str:
    """Format a retrieved Qdrant document as a markdown snippet for the LLM.

    Query-example documents receive a ``sparql`` language tag that includes a
    ``#+ endpoint:`` comment, matching the format expected by the
    ``SYSTEM_PROMPT``.  Schema documents use a plain (untagged) code block.

    Args:
        doc: A scored Qdrant point whose ``payload`` contains at least
            ``question`` and ``answer`` keys.

    Returns:
        A markdown-formatted string ready to be injected into the system prompt.
    """
    payload = doc.payload or {}
    doc_lang = (
        f"sparql\n#+ endpoint: {payload.get('endpoint_url', 'not provided')}"
        if "query" in payload.get("doc_type", "")
        else ""
    )
    return (
        f"\n{payload['question']} ({payload.get('endpoint_url', '')}):\n\n"
        f"```{doc_lang}\n{payload.get('answer')}\n```\n\n"
    )
