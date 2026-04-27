"""LLM provider factory for the SPARQL Query Assistant."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel


def load_chat_model(model: str) -> BaseChatModel:
    """Instantiate a chat model from a ``'provider/model-name'`` string.

    Supported providers: ``'mistralai'``, ``'groq'``.

    Args:
        model: Provider and model name separated by ``/``, e.g.
            ``'mistralai/mistral-small-latest'`` or
            ``'groq/llama-3.1-8b-instant'``.

    Returns:
        A LangChain ``BaseChatModel`` instance.

    Raises:
        ValueError: If the provider prefix is not recognised.
    """
    provider, model_name = model.split("/", maxsplit=1)
    if provider == "mistralai":
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(  # type: ignore[call-arg]
            model=model_name,
            temperature=0,
            max_tokens=1024,
        )
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model_name,
            temperature=0,
            max_tokens=1024,
        )
    raise ValueError(f"Unknown provider: {provider}")
