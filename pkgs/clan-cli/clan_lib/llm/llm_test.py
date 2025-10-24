from collections.abc import Callable

import pytest
from clan_cli.tests.fixtures_flakes import nested_dict
from clan_lib.flake.flake import Flake
from clan_lib.llm.phases import llm_final_decision_to_inventory_instances
from clan_lib.llm.schemas import (
    FunctionCallType,
    OpenAIFunctionSchema,
    aggregate_openai_function_schemas,
    clan_module_to_openai_spec,
)
from clan_lib.services.modules import list_service_modules


@pytest.mark.with_core
def test_clan_module_to_llm_func(
    clan_flake: Callable[..., Flake],
) -> None:
    # ATTENTION! This method lacks Typechecking
    config = nested_dict()
    # explicit module selection
    # We use this random string in test to avoid code dependencies on the input name
    config["inventory"]["instances"]["foo"]["module"]["input"] = (
        "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"
    )
    config["inventory"]["instances"]["foo"]["module"]["name"] = "sshd"
    # input = null
    config["inventory"]["instances"]["bar"]["module"]["input"] = None
    config["inventory"]["instances"]["bar"]["module"]["name"] = "sshd"

    config["inventory"]["machines"] = {
        "machine1": {
            "tags": ["production", "backup"],
        },
        "machine2": {
            "tags": ["client"],
        },
        "machine3": {
            "tags": ["client"],
        },
    }
    config["inventory"]["tags"] = {
        "production": [],
        "backup": [],
        "client": [],
    }

    # Omit input
    config["inventory"]["instances"]["baz"]["module"]["name"] = "sshd"
    # external input
    flake = clan_flake(config)

    service_modules = list_service_modules(flake)

    # Module(usage_ref={'name': 'borgbackup', 'input': None}, info=ModuleInfo(manifest=ModuleManifest(name='borgbackup', description='Efficient, deduplicating backup program with optional compression and secure encryption.', categories=['System'], features={'API': True}), roles={'client': Role(name='client', description='A borgbackup client that backs up to all borgbackup server roles.'), 'server': Role(name='server', description='A borgbackup server that stores the backups of clients.')}), native=True, instance_refs=[]),
    borgbackup_service = next(
        m for m in service_modules.modules if m.usage_ref.get("name") == "borgbackup"
    )

    assert borgbackup_service is not None

    available_machines = ["machine1", "machine2", "server1"]
    available_tags = ["production", "backup", "client"]

    generated_tool_func = clan_module_to_openai_spec(
        borgbackup_service, available_tags, available_machines
    )

    expected_tool_func: OpenAIFunctionSchema = {
        "type": "function",
        "name": "borgbackup",
        "description": "Efficient, deduplicating backup program with optional compression and secure encryption.",
        "parameters": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "object",
                    "properties": {},
                },
                "roles": {
                    "type": "object",
                    "properties": {
                        "client": {
                            "type": "object",
                            "description": "A borgbackup client that backs up to all borgbackup server roles.",
                            "properties": {
                                "machines": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(machine1|machine2|server1)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Machines to assign this role to. Format: each machine name is a key with an empty object {} as value. Example: {"wintux": {}, "gchq-local": {}}',
                                },
                                "tags": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(production|backup|client)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Tags to assign this role to. Format: each tag name is a key with an empty object {} as value. Example: {"all": {}, "nixos": {}}',
                                },
                            },
                            "additionalProperties": False,
                        },
                        "server": {
                            "type": "object",
                            "description": "A borgbackup server that stores the backups of clients.",
                            "properties": {
                                "machines": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(machine1|machine2|server1)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Machines to assign this role to. Format: each machine name is a key with an empty object {} as value. Example: {"wintux": {}, "gchq-local": {}}',
                                },
                                "tags": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(production|backup|client)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Tags to assign this role to. Format: each tag name is a key with an empty object {} as value. Example: {"all": {}, "nixos": {}}',
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": ["roles"],
            "additionalProperties": False,
        },
        "strict": True,
    }

    assert generated_tool_func == expected_tool_func

    certificate_service = next(
        m for m in service_modules.modules if m.usage_ref.get("name") == "certificates"
    )
    assert certificate_service is not None

    generated_tool_func2 = clan_module_to_openai_spec(
        certificate_service, available_tags, available_machines
    )

    expected_tool_func2: OpenAIFunctionSchema = {
        "type": "function",
        "name": "certificates",
        "description": "Sets up a PKI certificate chain using step-ca",
        "parameters": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "object",
                    "properties": {},
                },
                "roles": {
                    "type": "object",
                    "properties": {
                        "ca": {
                            "type": "object",
                            "description": "A certificate authority that issues and signs certificates for other machines.",
                            "properties": {
                                "machines": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(machine1|machine2|server1)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Machines to assign this role to. Format: each machine name is a key with an empty object {} as value. Example: {"wintux": {}, "gchq-local": {}}',
                                },
                                "tags": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(production|backup|client)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Tags to assign this role to. Format: each tag name is a key with an empty object {} as value. Example: {"all": {}, "nixos": {}}',
                                },
                            },
                            "additionalProperties": False,
                        },
                        "default": {
                            "type": "object",
                            "description": "A machine that trusts the CA and can get certificates issued by it.",
                            "properties": {
                                "machines": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(machine1|machine2|server1)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Machines to assign this role to. Format: each machine name is a key with an empty object {} as value. Example: {"wintux": {}, "gchq-local": {}}',
                                },
                                "tags": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^(production|backup|client)$": {
                                            "type": "object",
                                            "additionalProperties": False,
                                        }
                                    },
                                    "additionalProperties": False,
                                    "description": 'Tags to assign this role to. Format: each tag name is a key with an empty object {} as value. Example: {"all": {}, "nixos": {}}',
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": ["roles"],
            "additionalProperties": False,
        },
        "strict": True,
    }

    assert generated_tool_func2 == expected_tool_func2

    aggregate = aggregate_openai_function_schemas(flake)

    assert len(aggregate.tools) >= 2


def test_llm_final_decision_to_inventory_conversion() -> None:
    """Test conversion of LLM final decision to inventory format."""
    final_decision: list[FunctionCallType] = [
        {
            "id": "toolu_01XHjHUMzZVTcDCqaYQJEWu5",
            "call_id": "toolu_01XHjHUMzZVTcDCqaYQJEWu5",
            "type": "function_call",
            "name": "matrix-synapse",
            "arguments": '{"roles": {"default": {"machines": {"gchq-local": {}}}}}',
        },
        {
            "id": "toolu_01TsjKZ87J3fi6RNzNzu33ff",
            "call_id": "toolu_01TsjKZ87J3fi6RNzNzu33ff",
            "type": "function_call",
            "name": "monitoring",
            "arguments": '{"module": { "input": "qubasas-clan" }, "roles": {"telegraf": {"tags": {"all": {}}}}}',
        },
    ]
    assert isinstance(final_decision, list)

    expected = [
        {
            "module": {
                "input": None,
                "name": "matrix-synapse",
            },
            "roles": {"default": {"machines": {"gchq-local": {}}}},
        },
        {
            "module": {
                "input": "qubasas-clan",
                "name": "monitoring",
            },
            "roles": {"telegraf": {"tags": {"all": {}}}},
        },
    ]

    result = llm_final_decision_to_inventory_instances(final_decision)
    assert result == expected
