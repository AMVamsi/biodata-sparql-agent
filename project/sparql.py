"""SPARQL query extraction and execution."""

from __future__ import annotations

from sparql_llm.utils import query_sparql
from sparql_llm.validate_sparql import extract_sparql_queries


def execute_query(last_msg: str) -> list[dict[str, str]] | None:
    """Extract a SPARQL query from an LLM response and execute it.

    Parses the first valid ``#+ endpoint:`` annotated SPARQL block found in
    *last_msg*, then executes the query against the declared endpoint.

    Args:
        last_msg: The raw LLM response string, expected to contain a fenced
            SPARQL code block with a ``#+ endpoint:`` comment.

    Returns:
        A list of result bindings (each binding is a ``dict[str, str]``), or
        ``None`` if no executable SPARQL block was found.
    """
    for extracted_query in extract_sparql_queries(last_msg):
        query = extracted_query.get("query")
        endpoint_url = extracted_query.get("endpoint_url")
        if query and endpoint_url:
            res = query_sparql(query, endpoint_url)
            return res.get("results", {}).get("bindings", [])
    return None
