from typing import Any, Literal, TypedDict

from clan_lib.services.modules import Module

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


class JSONSchemaProperty(TypedDict, total=False):
    type: JSONSchemaType | list[JSONSchemaType]
    format: JSONSchemaFormat
    description: str | None
    enum: list[str] | None
    items: dict[str, Any] | None
    properties: dict[str, "JSONSchemaProperty"] | None
    patternProperties: dict[str, "JSONSchemaProperty"] | None
    required: list[str] | None
    additionalProperties: bool | dict[str, Any] | None


class JSONSchemaParameters(TypedDict, total=False):
    type: JSONSchemaType
    properties: dict[str, JSONSchemaProperty]
    required: list[str]
    additionalProperties: bool


class LLMFunctionSchema(TypedDict):
    type: Literal["function"]
    name: str
    description: str
    parameters: JSONSchemaParameters
    strict: bool


def clan_module_to_llm_function(
    module: Module, available_tags: list[str], available_machines: list[str]
) -> LLMFunctionSchema:
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
                    description="Machines for this role with empty configuration objects",
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
                    description="Tags for this role with empty configuration objects",
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

    return LLMFunctionSchema(
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
