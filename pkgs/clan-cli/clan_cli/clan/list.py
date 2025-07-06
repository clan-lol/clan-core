import argparse
import logging

from clan_lib.templates import list_templates

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    templates = list_templates(args.flake)

    builtin_clan_templates = templates.builtins.get("clan", {})

    print("Available templates")
    print("├── <builtin>")
    for i, (name, template) in enumerate(builtin_clan_templates.items()):
        is_last_template = i == len(builtin_clan_templates.items()) - 1
        if not is_last_template:
            print(f"│   ├── {name}: {template.get('description', 'no description')}")
        else:
            print(f"│   └── {name}: {template.get('description', 'no description')}")

    for i, (input_name, input_templates) in enumerate(templates.custom.items()):
        custom_clan_templates = input_templates.get("clan", {})
        is_last_input = i == len(templates.custom.items()) - 1
        prefix = "│" if not is_last_input else " "
        if not is_last_input:
            print(f"├── inputs.{input_name}:")
        else:
            print(f"└── inputs.{input_name}:")

        for i, (name, template) in enumerate(custom_clan_templates.items()):
            is_last_template = i == len(builtin_clan_templates.items()) - 1
            if not is_last_template:
                print(
                    f"{prefix}   ├── {name}: {template.get('description', 'no description')}"
                )
            else:
                print(
                    f"{prefix}   └── {name}: {template.get('description', 'no description')}"
                )


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
