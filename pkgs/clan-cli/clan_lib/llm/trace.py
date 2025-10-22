"""LLM conversation tracing for debugging and analysis."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from .schemas import ChatMessage

log = logging.getLogger(__name__)


def write_trace_entry(
    trace_file: Path,
    provider: Literal["openai", "ollama", "claude"],
    model: str,
    stage: str,
    request: dict[str, Any],
    response: dict[str, Any],
    duration_ms: float,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Write a single trace entry to the trace file.

    The trace file is appended to (not overwritten) to create a linear log
    of all LLM interactions during a session.

    Args:
        trace_file: Path to the JSON trace file
        provider: The LLM provider used
        model: The model name
        stage: The stage/phase of processing (e.g., "discovery", "final_decision")
        request: The request data sent to the LLM (messages, tools, etc.)
        response: The response data from the LLM (function_calls, message, etc.)
        duration_ms: Duration of the API call in milliseconds
        metadata: Optional metadata to include in the trace entry

    """
    timestamp = datetime.now(UTC).isoformat()

    entry = {
        "timestamp": timestamp,
        "provider": provider,
        "model": model,
        "stage": stage,
        "request": request,
        "response": response,
        "duration_ms": round(duration_ms, 2),
    }
    if metadata:
        entry["metadata"] = metadata

    try:
        # Read existing entries if file exists
        existing_entries: list[dict[str, Any]] = []
        if trace_file.exists():
            with trace_file.open("r") as f:
                try:
                    existing_entries = json.load(f)
                    if not isinstance(existing_entries, list):
                        log.warning(
                            f"Trace file {trace_file} is not a list, starting fresh"
                        )
                        existing_entries = []
                except json.JSONDecodeError:
                    log.warning(
                        f"Trace file {trace_file} is invalid JSON, starting fresh"
                    )
                    existing_entries = []

        # Append new entry
        existing_entries.append(entry)

        # Write back with nice formatting
        trace_file.parent.mkdir(parents=True, exist_ok=True)
        with trace_file.open("w") as f:
            json.dump(existing_entries, f, indent=2, ensure_ascii=False)

        log.info(f"Wrote trace entry to {trace_file} (stage: {stage})")

    except (OSError, json.JSONDecodeError):
        log.exception(f"Failed to write trace entry to {trace_file}")


def format_messages_for_trace(messages: list[ChatMessage]) -> list[dict[str, str]]:
    """Format chat messages for human-readable trace output.

    Args:
        messages: List of chat messages

    Returns:
        List of formatted message dictionaries

    """
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]


def format_tools_for_trace(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Format tools for human-readable trace output.

    Simplifies tool schemas to just name and description for readability.

    Args:
        tools: List of tool definitions

    Returns:
        Simplified list of tool dictionaries

    """
    result = []
    for tool in tools:
        if "function" in tool:
            # OpenAI/Claude format
            func = tool["function"]
            result.append(
                {
                    "name": func.get("name"),
                    "description": func.get("description"),
                    "parameters": func.get("parameters", {}),
                }
            )
        else:
            # Other formats - just pass through
            result.append(tool)
    return result
