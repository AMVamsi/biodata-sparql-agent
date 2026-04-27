"""SPARQL Query Assistant — Chainlit entry point.

This module wires together the LLM, retrieval pipeline, and SPARQL executor
and exposes them as a Chainlit chat application.
"""

from __future__ import annotations

import json
import logging

import chainlit as cl

from config import MAX_TRY_COUNT, SYSTEM_PROMPT
from llm import load_chat_model
from retrieval import format_doc, retrieve_docs
from sparql import execute_query

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Active LLM — swap provider/model here or toggle to Groq:
# llm = load_chat_model("groq/meta-llama/llama-4-scout-17b-16e-instruct")
llm = load_chat_model("mistralai/mistral-small-latest")


@cl.on_message
async def on_message(msg: cl.Message) -> None:
    """Handle an incoming user message.

    Retrieves relevant SPARQL documents, calls the LLM, executes the generated
    query, and summarises the results.  Retries up to ``MAX_TRY_COUNT`` times
    if the first query returns no results.
    """
    retrieved_docs = retrieve_docs(msg.content)
    formatted_docs = "\n".join(format_doc(doc) for doc in retrieved_docs)
    async with cl.Step(name=f"{len(retrieved_docs)} relevant documents 📚️") as step:
        step.output = formatted_docs
    messages = [
        ("system", SYSTEM_PROMPT.format(relevant_docs=formatted_docs)),
        *cl.chat_context.to_openai(),
    ]

    query_success = False
    for _i in range(MAX_TRY_COUNT):
        answer = cl.Message(content="")
        for resp in llm.stream(messages):
            token = resp.content if isinstance(resp.content, str) else ""
            await answer.stream_token(token)
            if getattr(resp, "usage_metadata", None):
                logging.info(f"🎰 {resp.usage_metadata}")  # type: ignore[attr-defined]
        await answer.send()

        if query_success:
            break

        query_res = execute_query(answer.content)
        if not query_res:
            logging.warning("⚠️ No results, trying to fix")
            messages.append(
                (
                    "user",
                    f"""The query you provided returned no results, please fix the query:\n\n{answer.content}""",
                )
            )
        else:
            logging.info(
                f"✅ Got {len(query_res)} results! Summarizing them, then stopping the chat"
            )
            async with cl.Step(name=f"{len(query_res)} query results ✨") as step:
                step.output = f"```json\n{json.dumps(query_res, indent=2)}\n```"
            messages.append(
                (
                    "user",
                    f"""The query you provided returned these results, summarize them:\n\n{json.dumps(query_res, indent=2)}""",
                )
            )
            query_success = True


@cl.set_starters
async def set_starters(user: cl.User | None = None) -> list[cl.Starter]:
    """Return starter questions shown in the Chainlit UI."""
    return [
        cl.Starter(
            label="Rat orthologs",
            message="What are the rat orthologs of human TP53?",
        ),
    ]
