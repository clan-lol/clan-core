from collections.abc import Callable

import pytest
from clan_cli.tests.fixtures_flakes import nested_dict
from clan_lib.flake.flake import Flake
from clan_lib.services.llm import LLMFunctionSchema, clan_module_to_llm_function
from clan_lib.services.modules import (
    list_service_modules,
)


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

    generated_tool_func = clan_module_to_llm_function(
        borgbackup_service, available_tags, available_machines
    )

    expected_tool_func: LLMFunctionSchema = {
        "type": "function",
        "name": "borgbackup",
        "description": "Efficient, deduplicating backup program with optional compression and secure encryption.",
        "parameters": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "object",
                    "properties": {
                        # "input": {
                        #     "type": "string",
                        #     "description": "Source / Input name of the module, e.g. 'clan-core' or null for built-in modules",
                        #     "enum": ["Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"],
                        # }
                    },
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
                                    "description": "Machines for this role with empty configuration objects",
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
                                    "description": "Tags for this role with empty configuration objects",
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
                                    "description": "Machines for this role with empty configuration objects",
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
                                    "description": "Tags for this role with empty configuration objects",
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

    generated_tool_func2 = clan_module_to_llm_function(
        certificate_service, available_tags, available_machines
    )

    expected_tool_func2: LLMFunctionSchema = {
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
                                    "description": "Machines for this role with empty configuration objects",
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
                                    "description": "Tags for this role with empty configuration objects",
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
                                    "description": "Machines for this role with empty configuration objects",
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
                                    "description": "Tags for this role with empty configuration objects",
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
