"""Type definitions and schema conversion for LLM function calling."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

from clan_lib.errors import ClanError
from clan_lib.machines.list import list_machines
from clan_lib.services.modules import Module, list_service_modules
from clan_lib.tags.list import list_tags

if TYPE_CHECKING:
    from clan_lib.flake.flake import Flake

log = logging.getLogger(__name__)

JSONSchemaType = Literal[
    "array", "boolean", "integer", "null", "number", "object", "string"
]

JSONSchemaFormat = Literal[
    # Dates and Times
    "date-time",
    "time",
    "date",
    "duration",
    # Email Addresses
    "email",
    "idn-email",
    # Hostnames
    "hostname",
    "idn-hostname",
    # IP Addresses
    "ipv4",
    "ipv6",
    # Resource Identifiers
    "uuid",
    "uri",
    "uri-reference",
    "iri",
    "iri-reference",
    # URI Template
    "uri-template",
    # JSON Pointer
    "json-pointer",
    "relative-json-pointer",
    # Regular Expressions
    "regex",
]

JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]

JSONDict = dict[str, JSONValue]

MessageRole = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    role: MessageRole
    content: str
    mode: NotRequired[str]


ConversationHistory = list[ChatMessage]


class PendingDiscoveryState(TypedDict, total=False):
    user_request: NotRequired[str]


class PendingReadmeFetchState(TypedDict, total=False):
    readme_requests: NotRequired[list[dict[str, JSONValue]]]


class PendingServiceSelectionState(TypedDict, total=False):
    readme_results: NotRequired[list[dict[str, JSONValue]]]


class PendingFinalDecisionState(TypedDict, total=False):
    service_name: NotRequired[str]
    service_summary: NotRequired[str]


class SessionState(TypedDict, total=False):
    pending_discovery: NotRequired[PendingDiscoveryState]
    pending_readme_fetch: NotRequired[PendingReadmeFetchState]
    pending_service_selection: NotRequired[PendingServiceSelectionState]
    pending_final_decision: NotRequired[PendingFinalDecisionState]


class JSONSchemaProperty(TypedDict, total=False):
    type: JSONSchemaType | list[JSONSchemaType]
    format: JSONSchemaFormat
    description: str | None
    enum: list[str] | None
    items: JSONDict | None
    properties: dict[str, JSONSchemaProperty] | None
    patternProperties: dict[str, JSONSchemaProperty] | None
    required: list[str] | None
    additionalProperties: bool | JSONDict | None


class JSONSchemaParameters(TypedDict, total=False):
    type: JSONSchemaType
    properties: dict[str, JSONSchemaProperty]
    required: list[str]
    additionalProperties: bool


class OpenAIFunctionSchema(TypedDict):
    type: Literal["function"]
    name: str
    description: str
    parameters: JSONSchemaParameters
    strict: bool


class OllamaFunctionDefinition(TypedDict):
    """The function definition inside an Ollama tool."""

    name: str
    description: str
    parameters: JSONSchemaParameters


class OllamaFunctionSchema(TypedDict):
    """Ollama-compatible function schema format."""

    type: Literal["function"]
    function: OllamaFunctionDefinition


class SimplifiedServiceSchema(TypedDict):
    """Simplified service schema with just name and description."""

    name: str
    description: str
    input: str | None


ToolDefinition = OpenAIFunctionSchema | OllamaFunctionSchema


class FunctionCallType(TypedDict):
    """Function call format matching OpenAI's function calling structure."""

    id: str
    call_id: str
    type: Literal["function_call"]
    name: str
    arguments: str


class ReadmeRequest(TypedDict):
    """Request for README documentation."""

    input_name: str | None
    function_name: str


@dataclass(frozen=True)
class MachineDescription:
    name: str
    description: str | None


@dataclass(frozen=True)
class TagDescription:
    name: str
    description: str | None


class OpenAIMessageContentBlock(TypedDict, total=False):
    type: str
    text: NotRequired[str]


OpenAIMessageContent = str | list[OpenAIMessageContentBlock]


class OpenAIToolFunctionPayload(TypedDict, total=False):
    name: NotRequired[str]
    arguments: NotRequired[str]


class OpenAIToolCallPayload(TypedDict, total=False):
    id: NotRequired[str]
    function: NotRequired[OpenAIToolFunctionPayload]


class OpenAIChatMessagePayload(TypedDict, total=False):
    role: NotRequired[MessageRole]
    content: NotRequired[OpenAIMessageContent]
    tool_calls: NotRequired[list[OpenAIToolCallPayload]]


class OpenAIChoicePayload(TypedDict, total=False):
    message: NotRequired[OpenAIChatMessagePayload]


class OpenAIChatCompletionResponse(TypedDict, total=False):
    choices: NotRequired[list[OpenAIChoicePayload]]


class OllamaToolFunctionPayload(TypedDict, total=False):
    name: NotRequired[str]
    arguments: NotRequired[JSONValue]


class OllamaToolCallPayload(TypedDict, total=False):
    function: NotRequired[OllamaToolFunctionPayload]


class OllamaMessagePayload(TypedDict, total=False):
    role: NotRequired[str]
    content: NotRequired[JSONValue]
    tool_calls: NotRequired[list[OllamaToolCallPayload]]


class OllamaChatResponse(TypedDict, total=False):
    message: NotRequired[OllamaMessagePayload]


MessageContent = JSONValue | OpenAIMessageContent


class ChatCompletionRequestPayload(TypedDict, total=False):
    model: str
    messages: list[ChatMessage]
    tools: list[ToolDefinition]
    stream: NotRequired[bool]


@dataclass(frozen=True)
class AiAggregate[T]:
    machines: list[MachineDescription]
    tags: list[TagDescription]
    tools: list[T]


def clan_module_to_openai_spec(
    module: Module, available_tags: list[str], available_machines: list[str]
) -> OpenAIFunctionSchema:
    """Convert a clan module to OpenAI function schema format.

    Args:
        module: The module to convert
        available_tags: List of available tag names
        available_machines: List of available machine names

    Returns:
        OpenAI function schema

    """
    # Create individual role schemas with descriptions
    role_properties = {}
    for role_name, role_info in module.info.roles.items():
        role_properties[role_name] = JSONSchemaProperty(
            type="object",
            description=role_info.description,
            properties={
                "machines": JSONSchemaProperty(
                    type="object",
                    patternProperties={
                        f"^({'|'.join(available_machines)})$": JSONSchemaProperty(
                            type="object",
                            additionalProperties=False,
                        )
                    },
                    additionalProperties=False,
                    description='Machines to assign this role to. Format: each machine name is a key with an empty object {} as value. Example: {"wintux": {}, "gchq-local": {}}',
                ),
                "tags": JSONSchemaProperty(
                    type="object",
                    patternProperties={
                        f"^({'|'.join(available_tags)})$": JSONSchemaProperty(
                            type="object",
                            additionalProperties=False,
                        )
                    },
                    additionalProperties=False,
                    description='Tags to assign this role to. Format: each tag name is a key with an empty object {} as value. Example: {"all": {}, "nixos": {}}',
                ),
            },
            additionalProperties=False,
        )

    module_name = module.usage_ref.get("name")
    if not isinstance(module_name, str):
        msg = "Module name must be a string"
        raise TypeError(msg)

    module_input = module.usage_ref.get("input")
    if module_input is not None and not isinstance(module_input, str):
        msg = "Module input must be a string or None"
        raise TypeError(msg)

    module_properties = {}
    if module_input is not None:
        module_properties["input"] = JSONSchemaProperty(
            type="string",
            description=(
                "Source / Input name of the module, e.g. 'clan-core' or null for built-in modules"
            ),
            enum=[module_input],
        )

    return OpenAIFunctionSchema(
        type="function",
        name=module.usage_ref["name"],
        description=module.info.manifest.description,
        parameters=JSONSchemaParameters(
            type="object",
            properties={
                "module": JSONSchemaProperty(
                    type="object",
                    properties=module_properties,
                ),
                "roles": JSONSchemaProperty(
                    type="object",
                    properties=role_properties,
                    additionalProperties=False,
                ),
            },
            required=["roles"],
            additionalProperties=False,
        ),
        strict=True,
    )


def llm_function_to_ollama_format(
    llm_function: OpenAIFunctionSchema,
) -> OllamaFunctionSchema:
    """Convert OpenAI function schema to Ollama-compatible format.

    Args:
        llm_function: The OpenAI function schema to convert

    Returns:
        OllamaFunctionSchema with the function definition wrapped correctly

    """
    return OllamaFunctionSchema(
        type="function",
        function=OllamaFunctionDefinition(
            name=llm_function["name"],
            description=llm_function["description"],
            parameters=llm_function["parameters"],
        ),
    )


def aggregate_openai_function_schemas(
    flake: Flake,
) -> AiAggregate[OpenAIFunctionSchema]:
    """Collect all service modules and convert them to OpenAI function schemas.

    Args:
        flake: The Flake object to extract services from

    Returns:
        AiAggregate containing machines, tags, and OpenAI function schemas

    Raises:
        ClanError: If no machines or tags are found

    """
    # Extract machine names
    machines = list_machines(flake)
    available_machines = list(machines.keys())

    # If no machines exist, raise error
    if not available_machines:
        msg = "No machines found in inventory. Please add at least one machine."
        raise ClanError(msg)

    # Extract tags from all machines
    all_tags = list_tags(flake)
    available_tags: set[str] = all_tags.options
    available_tags.update(all_tags.special)

    if not available_tags:
        msg = "No tags found in inventory. Please add at least one tag."
        raise ClanError(msg)

    # List all service modules
    service_modules = list_service_modules(flake)

    # Convert each module to OpenAI function schema
    tools: list[OpenAIFunctionSchema] = []
    for module in service_modules.modules:
        llm_function: OpenAIFunctionSchema = clan_module_to_openai_spec(
            module, list(available_tags), available_machines
        )
        tools.append(llm_function)

    tags_with_descriptions: list[TagDescription] = []

    for tag in sorted(available_tags):
        new_tag = TagDescription(name=tag, description=None)
        if tag in all_tags.special:
            match tag:
                case "all":
                    new_tag = TagDescription(
                        name=tag, description="A group containing all machines"
                    )
                case "darwin":
                    new_tag = TagDescription(
                        name=tag, description="A group containing all macOS machines"
                    )
                case "nixos":
                    new_tag = TagDescription(
                        name=tag, description="A group containing all NixOS machines"
                    )
                case _:
                    log.error(
                        f"Unhandled special tag: {tag}, dropping from llm context"
                    )
        else:
            log.warning(
                f"Reading tag descriptions is not yet implemented, setting to None for: {tag}"
                "This might result in the LLM not using this tag appropriately."
            )
        tags_with_descriptions.append(new_tag)

    return AiAggregate(
        machines=[
            MachineDescription(
                name=m.data["name"], description=m.data.get("description")
            )
            for m in machines.values()
        ],
        tags=tags_with_descriptions,
        tools=tools,
    )


def aggregate_ollama_function_schemas(
    flake: Flake,
) -> AiAggregate[OllamaFunctionSchema]:
    """Collect all service modules and convert them to Ollama function schemas.

    Args:
        flake: The Flake object to extract services from

    Returns:
        AiAggregate containing machines, tags, and Ollama function schemas

    """
    openai_schemas = aggregate_openai_function_schemas(flake)
    ollama_schemas = [llm_function_to_ollama_format(f) for f in openai_schemas.tools]
    return AiAggregate(
        machines=openai_schemas.machines, tags=openai_schemas.tags, tools=ollama_schemas
    )


def create_simplified_service_schemas(flake: Flake) -> list[SimplifiedServiceSchema]:
    """Create simplified schemas with just names and descriptions for initial LLM pass.

    Args:
        flake: The Flake object to extract services from

    Returns:
        List of simplified service schemas

    """
    service_modules = list_service_modules(flake)
    simplified: list[SimplifiedServiceSchema] = []

    for module in service_modules.modules:
        module_input = module.usage_ref.get("input")
        if module_input is not None and not isinstance(module_input, str):
            msg = "Module input must be a string or None"
            raise TypeError(msg)

        simplified.append(
            SimplifiedServiceSchema(
                name=module.usage_ref["name"],
                description=module.info.manifest.description,
                input=module_input,
            )
        )

    return simplified


def create_get_readme_tool(
    valid_function_names: list[str],
) -> OllamaFunctionSchema:
    """Create the get_readme tool schema for querying service details.

    Args:
        valid_function_names: List of service function names that may be requested

    Returns:
        The get_readme tool in Ollama format

    """
    sorted_names = sorted(valid_function_names)
    return OllamaFunctionSchema(
        type="function",
        function=OllamaFunctionDefinition(
            name="get_readme",
            description="Retrieve detailed documentation (README) for a specific service/module to learn more about its roles, configuration, and requirements before deciding to use it.",
            parameters=JSONSchemaParameters(
                type="object",
                properties={
                    "input_name": JSONSchemaProperty(
                        type=["string", "null"],
                        description="The input/source name of the module (e.g., 'clan-core'). Use null for built-in modules.",
                    ),
                    "function_name": JSONSchemaProperty(
                        type="string",
                        description="The name of the service/function to get documentation for (e.g., 'zerotier', 'postgresql').",
                        enum=sorted_names,
                    ),
                },
                required=["function_name"],
            ),
        ),
    )


def create_select_service_tool(
    available_services: list[str],
) -> OllamaFunctionSchema:
    """Create the select_service tool schema for selecting one service from candidates.

    Args:
        available_services: List of service names to choose from

    Returns:
        The select_service tool in Ollama format

    """
    sorted_names = sorted(available_services)
    return OllamaFunctionSchema(
        type="function",
        function=OllamaFunctionDefinition(
            name="select_service",
            description="Select exactly one service from the available candidates and provide a focused summary of its documentation relevant to the user request.",
            parameters=JSONSchemaParameters(
                type="object",
                properties={
                    "service_name": JSONSchemaProperty(
                        type="string",
                        description="The name of the selected service. Must match one of the available service names exactly.",
                        enum=sorted_names,
                    ),
                    "summary": JSONSchemaProperty(
                        type="string",
                        description="A concise summary (max 300 words) focusing on: (1) VALUE PROPOSITION - what problem this service solves and why you'd use it, (2) ROLES - what roles exist and the PURPOSE of each role, (3) KEY CONSTRAINTS - critical dependencies or limitations. Do NOT copy README examples or configuration snippets. Synthesize WHAT the service does and WHY, not HOW to configure it.",
                    ),
                },
                required=["service_name", "summary"],
            ),
        ),
    )
