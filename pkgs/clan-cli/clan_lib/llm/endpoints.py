"""API client code for LLM providers (OpenAI and Ollama)."""

import json
import logging
import os
import time
import urllib.request
from collections.abc import Sequence
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError

from clan_lib.errors import ClanError

from .schemas import (
    ChatCompletionRequestPayload,
    ChatMessage,
    FunctionCallType,
    MessageContent,
    OllamaChatResponse,
    OpenAIChatCompletionResponse,
    ToolDefinition,
)
from .trace import (
    format_messages_for_trace,
    format_tools_for_trace,
    write_trace_entry,
)

log = logging.getLogger(__name__)


def _stringify_message_content(content: MessageContent | None) -> str:
    """Convert message content payloads to human-readable text for logging."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text_part = item.get("text")
                if isinstance(text_part, str):
                    parts.append(text_part)
                    continue
            parts.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(parts)
    return json.dumps(content, ensure_ascii=False)


def _summarize_tools(
    tools: Sequence[ToolDefinition],
) -> str:
    """Create a concise comma-separated list of tool names for logging."""
    names: list[str] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        function_block = tool.get("function")
        if isinstance(function_block, dict) and "name" in function_block:
            name = function_block.get("name")
        else:
            name = tool.get("name")
        if isinstance(name, str):
            names.append(name)
    return ", ".join(names)


def _debug_log_request(
    provider: str,
    messages: list[ChatMessage],
    tools: Sequence[ToolDefinition],
) -> None:
    """Emit structured debug logs for outbound LLM requests."""
    if not log.isEnabledFor(logging.DEBUG):
        return

    log.debug("[%s] >>> sending %d message(s)", provider, len(messages))
    for idx, message in enumerate(messages):
        role = message.get("role", "unknown")
        content_str = _stringify_message_content(message.get("content"))
        log.debug(
            "[%s] >>> message[%02d] role=%s len=%d",
            provider,
            idx,
            role,
            len(content_str),
        )
        if content_str:
            log.debug("[%s] >>> message[%02d] content:\n%s", provider, idx, content_str)

    if tools:
        log.debug("[%s] >>> tool summary: %s", provider, _summarize_tools(tools))
        log.debug(
            "[%s] >>> tool payload:\n%s",
            provider,
            json.dumps(list(tools), indent=2, ensure_ascii=False),
        )


def _debug_log_response(
    provider: str,
    text: str,
    function_calls: list[FunctionCallType],
) -> None:
    """Emit structured debug logs for inbound LLM responses."""
    if not log.isEnabledFor(logging.DEBUG):
        return

    if text:
        log.debug(
            "[%s] <<< response text len=%d\n%s",
            provider,
            len(text),
            text,
        )
    else:
        log.debug("[%s] <<< no textual response", provider)

    if not function_calls:
        log.debug("[%s] <<< no function calls", provider)
        return

    for idx, call in enumerate(function_calls):
        args_repr = call.get("arguments", "")
        formatted_args = args_repr
        if isinstance(args_repr, str):
            try:
                parsed_args = json.loads(args_repr)
                formatted_args = json.dumps(parsed_args, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                formatted_args = args_repr
        log.debug(
            "[%s] <<< call[%02d] name=%s\n%s",
            provider,
            idx,
            call.get("name"),
            formatted_args,
        )


def call_openai_api(
    model: str,
    messages: list[ChatMessage],
    tools: Sequence[ToolDefinition],
    timeout: int = 60,
    trace_file: Path | None = None,
    stage: str = "unknown",
    trace_metadata: dict[str, Any] | None = None,
) -> OpenAIChatCompletionResponse:
    """Call the OpenAI API for chat completion.

    Args:
        model: The OpenAI model to use
        messages: List of message dictionaries
        tools: List of OpenAI function schemas
        timeout: Request timeout in seconds (default: 60)
        trace_file: Optional path to write trace entries for debugging
        stage: Stage name for trace entries (default: "unknown")
        trace_metadata: Optional metadata to include in trace entries

    Returns:
        The parsed JSON response from the API

    Raises:
        ClanError: If the API call fails

    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        msg = "OPENAI_API_KEY environment variable is required for OpenAI provider"
        raise ClanError(msg)

    payload: ChatCompletionRequestPayload = {
        "model": model,
        "messages": messages,
        "tools": list(tools),
    }
    _debug_log_request("openai", messages, tools)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    start_time = time.time()
    try:
        req = urllib.request.Request(  # noqa: S310
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            if resp.getcode() != HTTPStatus.OK.value:
                msg = f"OpenAI API returned status {resp.getcode()}"
                raise ClanError(msg)

            raw = resp.read().decode("utf-8")
            response = cast("OpenAIChatCompletionResponse", json.loads(raw))

            # Write trace if requested
            if trace_file:
                duration_ms = (time.time() - start_time) * 1000
                function_calls, message_content = parse_openai_response(
                    response, provider="openai"
                )
                write_trace_entry(
                    trace_file=trace_file,
                    provider="openai",
                    model=model,
                    stage=stage,
                    request={
                        "messages": format_messages_for_trace(messages),
                        "tools": format_tools_for_trace(
                            cast("list[dict[str, Any]]", list(tools))
                        ),
                    },
                    response={
                        "function_calls": [
                            {
                                "name": call["name"],
                                "arguments": json.loads(call["arguments"])
                                if isinstance(call["arguments"], str)
                                else call["arguments"],
                            }
                            for call in function_calls
                        ],
                        "message": message_content,
                    },
                    duration_ms=duration_ms,
                    metadata=trace_metadata,
                )

            return response

    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        msg = f"OpenAI returned HTTP {e.code}: {error_body}"
        raise ClanError(msg) from e
    except URLError as e:
        msg = "OpenAI API not reachable"
        raise ClanError(msg) from e
    except json.JSONDecodeError as e:
        msg = "Failed to parse OpenAI API response"
        raise ClanError(msg) from e


def call_claude_api(
    model: str,
    messages: list[ChatMessage],
    tools: Sequence[ToolDefinition],
    base_url: str | None = None,
    timeout: int = 60,
    trace_file: Path | None = None,
    stage: str = "unknown",
    trace_metadata: dict[str, Any] | None = None,
) -> OpenAIChatCompletionResponse:
    """Call the Claude API (via OpenAI-compatible endpoint) for chat completion.

    Args:
        model: The Claude model to use
        messages: List of message dictionaries
        tools: List of function schemas (OpenAI format)
        base_url: Optional base URL for the API (defaults to https://api.anthropic.com/v1/)
        timeout: Request timeout in seconds (default: 60)
        trace_file: Optional path to write trace entries for debugging
        stage: Stage name for trace entries (default: "unknown")
        trace_metadata: Optional metadata to include in trace entries

    Returns:
        The parsed JSON response from the API

    Raises:
        ClanError: If the API call fails

    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        msg = "ANTHROPIC_API_KEY environment variable is required for Claude provider"
        raise ClanError(msg)

    if base_url is None:
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/")

    # Ensure base_url ends with /
    if not base_url.endswith("/"):
        base_url += "/"

    payload: ChatCompletionRequestPayload = {
        "model": model,
        "messages": messages,
        "tools": list(tools),
    }
    _debug_log_request("claude", messages, tools)

    url = f"{base_url}chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    start_time = time.time()
    try:
        req = urllib.request.Request(  # noqa: S310
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            if resp.getcode() != HTTPStatus.OK.value:
                msg = f"Claude API returned status {resp.getcode()}"
                raise ClanError(msg)

            raw = resp.read().decode("utf-8")
            response = cast("OpenAIChatCompletionResponse", json.loads(raw))

            # Write trace if requested
            if trace_file:
                duration_ms = (time.time() - start_time) * 1000
                function_calls, message_content = parse_openai_response(
                    response, provider="claude"
                )
                write_trace_entry(
                    trace_file=trace_file,
                    provider="claude",
                    model=model,
                    stage=stage,
                    request={
                        "messages": format_messages_for_trace(messages),
                        "tools": format_tools_for_trace(
                            cast("list[dict[str, Any]]", list(tools))
                        ),
                    },
                    response={
                        "function_calls": [
                            {
                                "name": call["name"],
                                "arguments": json.loads(call["arguments"])
                                if isinstance(call["arguments"], str)
                                else call["arguments"],
                            }
                            for call in function_calls
                        ],
                        "message": message_content,
                    },
                    duration_ms=duration_ms,
                    metadata=trace_metadata,
                )

            return response

    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        msg = f"Claude returned HTTP {e.code}: {error_body}"
        raise ClanError(msg) from e
    except URLError as e:
        msg = f"Claude API not reachable at {url}"
        raise ClanError(msg) from e
    except json.JSONDecodeError as e:
        msg = "Failed to parse Claude API response"
        raise ClanError(msg) from e


def call_ollama_api(
    model: str,
    messages: list[ChatMessage],
    tools: Sequence[ToolDefinition],
    timeout: int = 120,
    trace_file: Path | None = None,
    stage: str = "unknown",
    max_tokens: int | None = None,
    trace_metadata: dict[str, Any] | None = None,
) -> OllamaChatResponse:
    """Call the Ollama API for chat completion.

    Args:
        model: The Ollama model to use
        messages: List of message dictionaries
        tools: List of Ollama function schemas
        timeout: Request timeout in seconds (default: 120)
        trace_file: Optional path to write trace entries for debugging
        stage: Stage name for trace entries (default: "unknown")
        max_tokens: Maximum number of tokens to generate (default: None = unlimited)
        trace_metadata: Optional metadata to include in trace entries

    Returns:
        The parsed JSON response from the API

    Raises:
        ClanError: If the API call fails

    """
    payload: ChatCompletionRequestPayload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "tools": list(tools),
    }

    # Add max_tokens limit if specified
    if max_tokens is not None:
        payload["options"] = {"num_predict": max_tokens}  # type: ignore[typeddict-item]
    _debug_log_request("ollama", messages, tools)
    url = "http://localhost:11434/api/chat"

    start_time = time.time()
    try:
        req = urllib.request.Request(  # noqa: S310
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            if resp.getcode() != HTTPStatus.OK.value:
                msg = f"Ollama API returned status {resp.getcode()}"
                raise ClanError(msg)

            raw = resp.read().decode("utf-8")
            response = cast("OllamaChatResponse", json.loads(raw))

            # Write trace if requested
            if trace_file:
                duration_ms = (time.time() - start_time) * 1000
                function_calls, message_content = parse_ollama_response(
                    response, provider="ollama"
                )
                write_trace_entry(
                    trace_file=trace_file,
                    provider="ollama",
                    model=model,
                    stage=stage,
                    request={
                        "messages": format_messages_for_trace(messages),
                        "tools": format_tools_for_trace(
                            cast("list[dict[str, Any]]", list(tools))
                        ),
                    },
                    response={
                        "function_calls": [
                            {
                                "name": call["name"],
                                "arguments": json.loads(call["arguments"])
                                if isinstance(call["arguments"], str)
                                else call["arguments"],
                            }
                            for call in function_calls
                        ],
                        "message": message_content,
                    },
                    duration_ms=duration_ms,
                    metadata=trace_metadata,
                )

            return response

    except HTTPError as e:
        msg = f"Ollama returned HTTP {e.code} when requesting chat completion."
        raise ClanError(msg) from e
    except URLError as e:
        msg = "Ollama API not reachable at http://localhost:11434"
        raise ClanError(msg) from e
    except json.JSONDecodeError as e:
        msg = "Failed to parse Ollama API response"
        raise ClanError(msg) from e


def parse_openai_response(
    response_data: OpenAIChatCompletionResponse,
    provider: str = "openai",
) -> tuple[list[FunctionCallType], str]:
    """Parse OpenAI API response to extract function calls.

    Args:
        response_data: The raw response from OpenAI API
        provider: The provider name for logging purposes (default: "openai")

    Returns:
        Tuple of (function_calls, message_content)

    """
    choices = response_data.get("choices") or []
    if not choices:
        return [], ""

    message = choices[0].get("message") or {}
    tool_calls = message.get("tool_calls") or []
    raw_content = message.get("content") or ""
    model_content = _stringify_message_content(raw_content)

    result: list[FunctionCallType] = []
    for tool_call in tool_calls:
        tc_id = tool_call.get("id") or f"call_{int(time.time() * 1000)}"
        function = tool_call.get("function") or {}
        function_name = function.get("name") or ""
        function_args = function.get("arguments") or "{}"

        result.append(
            FunctionCallType(
                id=tc_id,
                call_id=tc_id,
                type="function_call",
                name=function_name,
                arguments=function_args,
            )
        )

    _debug_log_response(provider, model_content, result)

    return result, model_content


def parse_ollama_response(
    response_data: OllamaChatResponse,
    provider: str = "ollama",
) -> tuple[list[FunctionCallType], str]:
    """Parse Ollama API response to extract function calls.

    Args:
        response_data: The raw response from Ollama API
        provider: The provider name for logging purposes (default: "ollama")

    Returns:
        Tuple of (function_calls, message_content)

    """
    message = response_data.get("message") or {}
    tool_calls = message.get("tool_calls") or []
    raw_content = message.get("content") or ""
    model_content = _stringify_message_content(raw_content)

    result: list[FunctionCallType] = []
    for idx, tool_call in enumerate(tool_calls):
        function = tool_call.get("function") or {}
        function_name = function.get("name") or ""
        function_args = function.get("arguments") or {}

        # Generate unique IDs (similar to OpenAI format)
        call_id = f"call_{idx}_{int(time.time() * 1000)}"
        fc_id = f"fc_{idx}_{int(time.time() * 1000)}"

        result.append(
            FunctionCallType(
                id=fc_id,
                call_id=call_id,
                type="function_call",
                name=function_name,
                arguments=json.dumps(function_args),
            )
        )

    _debug_log_response(provider, model_content, result)

    return result, model_content
