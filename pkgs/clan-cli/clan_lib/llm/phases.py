"""Low-level LLM phase functions for orchestration."""

import json
import logging
from pathlib import Path
from typing import Literal

from clan_lib.errors import ClanAiError
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.clan import InventoryInstance
from clan_lib.services.modules import (
    InputName,
    ServiceName,
    ServiceReadmeCollection,
    get_service_readmes,
)

from .endpoints import (
    call_claude_api,
    call_ollama_api,
    call_openai_api,
    parse_ollama_response,
    parse_openai_response,
)
from .llm_types import ServiceSelectionResult, get_model_config
from .prompts import (
    build_discovery_prompt,
    build_final_decision_prompt,
    build_select_service_prompt,
)
from .schemas import (
    ChatMessage,
    ConversationHistory,
    FunctionCallType,
    JSONValue,
    ReadmeRequest,
    aggregate_ollama_function_schemas,
    aggregate_openai_function_schemas,
    create_get_readme_tool,
    create_select_service_tool,
    create_simplified_service_schemas,
)
from .utils import _strip_conversation_metadata, _user_message

log = logging.getLogger(__name__)


def get_llm_discovery_phase(
    user_request: str,
    flake: Flake,
    conversation_history: ConversationHistory | None = None,
    provider: Literal["openai", "ollama", "claude"] = "ollama",
    trace_file: Path | None = None,
    trace_metadata: dict[str, JSONValue] | None = None,
) -> tuple[list[ReadmeRequest], str]:
    """First LLM call: discovery phase with simplified schemas and get_readme tool.

    Args:
        user_request: The user's request/query
        flake: The Flake object to get services from
        conversation_history: Optional conversation history
        provider: The LLM provider to use
        trace_file: Optional path to write LLM interaction traces for debugging
        trace_metadata: Optional data to include in trace logs

    Returns:
        Tuple of (readme_requests, message_content):
            - readme_requests: List of readme requests from the LLM
            - message_content: Text response (e.g., questions or service recommendations)

    """
    # Get simplified services and create get_readme tool
    openai_aggregate = aggregate_openai_function_schemas(flake)
    simplified_services = create_simplified_service_schemas(flake)
    valid_function_names = [service["name"] for service in simplified_services]
    get_readme_tool = create_get_readme_tool(valid_function_names)

    # Build discovery prompt
    system_prompt, assistant_context = build_discovery_prompt(
        openai_aggregate.machines, openai_aggregate.tags, simplified_services
    )

    messages: list[ChatMessage] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": assistant_context},
    ]
    messages.extend(_strip_conversation_metadata(conversation_history))
    if user_request:
        messages.append(_user_message(user_request))

    # Call LLM with only get_readme tool
    model_config = get_model_config(provider)

    if provider == "openai":
        openai_response = call_openai_api(
            model_config.name,
            messages,
            [get_readme_tool],
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="discovery",
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_openai_response(
            openai_response, provider="openai"
        )
    elif provider == "claude":
        claude_response = call_claude_api(
            model_config.name,
            messages,
            [get_readme_tool],
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="discovery",
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_openai_response(
            claude_response, provider="claude"
        )
    else:
        ollama_response = call_ollama_api(
            model_config.name,
            messages,
            [get_readme_tool],
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="discovery",
            max_tokens=300,  # Limit output for discovery phase (get_readme calls or short question)
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_ollama_response(
            ollama_response, provider="ollama"
        )

    # Extract readme requests from function calls
    readme_requests: list[ReadmeRequest] = []
    for call in function_calls:
        if call["name"] == "get_readme":
            try:
                args = json.loads(call["arguments"])
                readme_requests.append(
                    ReadmeRequest(
                        input_name=args.get("input_name"),
                        function_name=args["function_name"],
                    )
                )
            except (json.JSONDecodeError, KeyError) as e:
                log.warning(f"Failed to parse readme request arguments: {e}")

    return readme_requests, message_content


def execute_readme_requests(
    requests: list[ReadmeRequest], flake: Flake
) -> dict[InputName, ServiceReadmeCollection]:
    """Execute readme requests and return results.

    Args:
        requests: List of readme requests
        flake: The Flake object

    Returns:
        Dictionary mapping input_name to ServiceReadmeCollection

    """
    results: dict[InputName, ServiceReadmeCollection] = {}
    requests_by_input: dict[InputName, list[ServiceName]] = {}

    # Group requests by input_name
    for req in requests:
        input_name = req["input_name"]
        if input_name not in requests_by_input:
            requests_by_input[input_name] = []
        requests_by_input[input_name].append(req["function_name"])

    # Fetch readmes for each input
    for input_name, service_names in requests_by_input.items():
        readme_collection = get_service_readmes(input_name, service_names, flake)
        results[input_name] = readme_collection

    return results


def get_llm_service_selection(
    user_request: str,
    readme_results: dict[InputName, ServiceReadmeCollection],
    conversation_history: ConversationHistory | None = None,
    provider: Literal["openai", "ollama", "claude"] = "ollama",
    trace_file: Path | None = None,
    trace_metadata: dict[str, JSONValue] | None = None,
) -> ServiceSelectionResult:
    """LLM call for service selection step: review READMEs and select one service.

    Args:
        user_request: The original user request
        readme_results: Dictionary of input_name -> ServiceReadmeCollection
        conversation_history: Optional conversation history
        provider: The LLM provider to use
        trace_file: Optional path to write LLM interaction traces for debugging
        trace_metadata: Optional data to include in trace logs

    Returns:
        ServiceSelectionResult with selected service info or clarifying question

    """
    # Build README context and collect service names
    readme_context = "README documentation for the following services:\n\n"
    available_services: list[str] = []
    for collection in readme_results.values():
        for service_name, readme_content in collection.readmes.items():
            available_services.append(service_name)
            if readme_content:  # Skip None values
                readme_context += f"=== {service_name} ===\n{readme_content}\n\n"

    readme_context = readme_context.rstrip()
    readme_context += "\n\n--- END OF README DOCUMENTATION ---"

    # Create select_service tool
    select_service_tool = create_select_service_tool(available_services)

    # Build prompt
    system_prompt, assistant_context = build_select_service_prompt(
        user_request, available_services
    )

    combined_assistant_context = (
        f"{assistant_context.rstrip()}\n\n{readme_context}"
        if assistant_context
        else readme_context
    )

    messages: list[ChatMessage] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": combined_assistant_context},
    ]
    messages.extend(_strip_conversation_metadata(conversation_history))
    if user_request:
        messages.append(_user_message(user_request))

    model_config = get_model_config(provider)

    # Call LLM
    if provider == "openai":
        openai_response = call_openai_api(
            model_config.name,
            messages,
            [select_service_tool],
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="select_service",
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_openai_response(
            openai_response, provider="openai"
        )
    elif provider == "claude":
        claude_response = call_claude_api(
            model_config.name,
            messages,
            [select_service_tool],
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="select_service",
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_openai_response(
            claude_response, provider="claude"
        )
    else:  # ollama
        ollama_response = call_ollama_api(
            model_config.name,
            messages,
            [select_service_tool],
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="select_service",
            max_tokens=600,  # Allow space for summary
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_ollama_response(
            ollama_response, provider="ollama"
        )

    # Check if LLM asked a clarifying question
    if message_content and not function_calls:
        return ServiceSelectionResult(
            selected_service=None,
            service_summary=None,
            clarifying_message=message_content,
        )

    # Extract service selection
    if function_calls:
        if len(function_calls) != 1:
            error_msg = (
                f"Expected exactly 1 select_service call, got {len(function_calls)}"
            )
            log.error(error_msg)
            return ServiceSelectionResult(
                selected_service=None,
                service_summary=None,
                clarifying_message=error_msg,
            )

        call = function_calls[0]
        if call["name"] != "select_service":
            error_msg = f"Expected select_service call, got {call['name']}"
            log.error(error_msg)
            return ServiceSelectionResult(
                selected_service=None,
                service_summary=None,
                clarifying_message=error_msg,
            )

        # Parse arguments
        try:
            args = (
                json.loads(call["arguments"])
                if isinstance(call["arguments"], str)
                else call["arguments"]
            )
            service_name = args.get("service_name")
            summary = args.get("summary")

            if not service_name or not summary:
                error_msg = "select_service call missing required fields"
                log.error(error_msg)
                return ServiceSelectionResult(
                    selected_service=None,
                    service_summary=None,
                    clarifying_message=error_msg,
                )

        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"Failed to parse select_service arguments: {e}"
            log.exception(error_msg)
            return ServiceSelectionResult(
                selected_service=None,
                service_summary=None,
                clarifying_message=error_msg,
            )
        else:
            return ServiceSelectionResult(
                selected_service=service_name,
                service_summary=summary,
                clarifying_message="",
            )

    # No function calls and no message - unexpected
    error_msg = "LLM did not select a service or ask for clarification"
    return ServiceSelectionResult(
        selected_service=None,
        service_summary=None,
        clarifying_message=error_msg,
    )


def get_llm_final_decision(
    user_request: str,
    flake: Flake,
    selected_service: str,
    service_summary: str,
    conversation_history: ConversationHistory | None = None,
    provider: Literal["openai", "ollama", "claude"] = "ollama",
    trace_file: Path | None = None,
    trace_metadata: dict[str, JSONValue] | None = None,
) -> tuple[list[FunctionCallType], str]:
    """Final LLM call: configure selected service with full schema.

    Args:
        user_request: The original user request
        flake: The Flake object
        selected_service: Name of the service selected in previous step
        service_summary: LLM-generated summary of the service documentation
        conversation_history: Optional conversation history
        provider: The LLM provider to use
        trace_file: Optional path to write LLM interaction traces for debugging
        trace_metadata: Optional data to include in trace logs

    Returns:
        Tuple of (function_calls, message_content)

    """
    # Get full schemas for ALL services, then filter to only the selected one
    all_schemas = aggregate_ollama_function_schemas(flake)

    # Filter to only include schema for the selected service
    filtered_tools = [
        tool
        for tool in all_schemas.tools
        if tool["function"]["name"] == selected_service
    ]

    if not filtered_tools:
        msg = f"No schema found for selected service: {selected_service}"
        raise ClanAiError(
            msg,
            description="The selected service does not have a schema available",
            location="Final Decision - Schema Lookup",
        )

    if len(filtered_tools) != 1:
        msg = f"Expected exactly 1 tool for service {selected_service}, got {len(filtered_tools)}"
        raise ClanAiError(
            msg,
            description="Service schema lookup returned unexpected results",
            location="Final Decision - Schema Lookup",
        )

    log.info(
        f"Configuring service: {selected_service} (providing ONLY this tool to LLM)"
    )

    # Prepare shared messages
    system_prompt, assistant_context = build_final_decision_prompt(
        all_schemas.machines, all_schemas.tags
    )

    # Build service summary message
    service_context = (
        f"Service documentation summary for `{selected_service}`:\n\n{service_summary}"
    )

    combined_assistant_context = (
        f"{assistant_context.rstrip()}\n\n{service_context}"
        if assistant_context
        else service_context
    )

    messages: list[ChatMessage] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": combined_assistant_context},
    ]
    messages.extend(_strip_conversation_metadata(conversation_history))
    if user_request:
        messages.append(_user_message(user_request))

    # Get full schemas
    model_config = get_model_config(provider)

    if provider == "openai":
        openai_response = call_openai_api(
            model_config.name,
            messages,
            filtered_tools,
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="final_decision",
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_openai_response(
            openai_response, provider="openai"
        )
        return function_calls, message_content

    if provider == "claude":
        claude_response = call_claude_api(
            model_config.name,
            messages,
            filtered_tools,
            timeout=model_config.timeout,
            trace_file=trace_file,
            stage="final_decision",
            trace_metadata=trace_metadata,
        )
        function_calls, message_content = parse_openai_response(
            claude_response, provider="claude"
        )
        return function_calls, message_content

    ollama_response = call_ollama_api(
        model_config.name,
        messages,
        filtered_tools,
        timeout=model_config.timeout,
        trace_file=trace_file,
        stage="final_decision",
        max_tokens=500,  # Limit output to prevent excessive verbosity
        trace_metadata=trace_metadata,
    )
    function_calls, message_content = parse_ollama_response(
        ollama_response, provider="ollama"
    )
    return function_calls, message_content


def llm_final_decision_to_inventory_instances(
    function_calls: list[FunctionCallType],
) -> list[InventoryInstance]:
    """Convert LLM function calls to an inventory instance list.

    Args:
        function_calls: List of function call dictionaries from the LLM

    Returns:
        List of inventory instances, each containing module metadata and roles

    """
    inventory_instances: list[InventoryInstance] = []

    for call in function_calls:
        func_name = call["name"]
        args = json.loads(call["arguments"])

        # Extract roles from arguments
        roles = args.get("roles", {})

        # Extract module input if present
        module_input = args.get("module", {}).get("input", None)

        # Create inventory instance for this module
        instance: InventoryInstance = {
            "module": {
                "input": module_input,
                "name": func_name,
            },
            "roles": roles,
        }
        inventory_instances.append(instance)

    return inventory_instances
