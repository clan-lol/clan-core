import argparse
import logging

from clan_lib.nix_models.clan import TemplateClanType
from clan_lib.templates import list_templates

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    templates = list_templates(args.flake)

    # Display all templates
    for i, (template_type, _builtin_template_set) in enumerate(
        templates.builtins.items()
    ):
        builtin_template_set: TemplateClanType | None = templates.builtins.get(
            template_type, None
        )  # type: ignore
        if not builtin_template_set:
            continue

        print(f"Available '{template_type}' templates")
        print("├── <builtin>")
        for i, (name, template) in enumerate(builtin_template_set.items()):
            description = template.get("description", "no description")
            is_last_template = i == len(builtin_template_set.items()) - 1
            if not is_last_template:
                print(f"│   ├── {name}: {description}")
            else:
                print(f"│   └── {name}: {description}")

        for i, (input_name, input_templates) in enumerate(templates.custom.items()):
            custom_templates: TemplateClanType | None = input_templates.get(
                template_type, None
            )  # type: ignore
            if not custom_templates:
                continue

            is_last_input = i == len(templates.custom.items()) - 1
            prefix = "│" if not is_last_input else " "
            if not is_last_input:
                print(f"├── inputs.{input_name}:")
            else:
                print(f"└── inputs.{input_name}:")

            for i, (name, template) in enumerate(custom_templates.items()):
                is_last_template = i == len(custom_templates.items()) - 1
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
