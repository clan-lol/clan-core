"""Utility helper functions for LLM orchestration."""

from typing import cast

from clan_lib.services.modules import InputName, ServiceReadmeCollection

from .schemas import ChatMessage, ConversationHistory, JSONValue

# Assistant mode constants
ASSISTANT_MODE_DISCOVERY = "discovery"
ASSISTANT_MODE_SELECTION = "service_selection"
ASSISTANT_MODE_FINAL = "final_decision"


def _assistant_message(content: str, mode: str | None = None) -> ChatMessage:
    """Create an assistant chat message with optional mode metadata."""
    message: ChatMessage = {"role": "assistant", "content": content}
    if mode:
        message["mode"] = mode
    return message


def _user_message(content: str) -> ChatMessage:
    """Create a user chat message."""
    return {"role": "user", "content": content}


def _strip_conversation_metadata(
    conversation_history: ConversationHistory | None,
) -> list[ChatMessage]:
    """Remove non-standard keys from conversation history before LLM calls."""
    if not conversation_history:
        return []
    return [
        {"role": message["role"], "content": message["content"]}
        for message in conversation_history
    ]


def _serialize_readme_results(
    readme_results: dict[InputName, ServiceReadmeCollection],
) -> list[dict[str, JSONValue]]:
    """Serialize readme results for storage in session state."""
    return [
        {
            "input_name": collection.input_name,
            "readmes": cast("dict[str, JSONValue]", collection.readmes),
        }
        for collection in readme_results.values()
    ]


def _deserialize_readme_results(
    data: list[dict[str, JSONValue]] | None,
) -> dict[InputName, ServiceReadmeCollection] | None:
    """Deserialize readme results from session state."""
    if data is None:
        return None

    results: dict[InputName, ServiceReadmeCollection] = {}
    for entry in data:
        input_name = entry.get("input_name")
        if input_name is not None and not isinstance(input_name, str):
            return None
        readmes_raw = entry.get("readmes")
        if not isinstance(readmes_raw, dict):
            return None

        typed_readmes: dict[str, str | None] = {}
        for service_name, content in readmes_raw.items():
            if not isinstance(service_name, str):
                return None
            if content is not None and not isinstance(content, str):
                return None
            typed_readmes[service_name] = content

        collection = ServiceReadmeCollection(
            input_name=input_name,
            readmes=typed_readmes,
        )
        results[input_name] = collection

    return results
