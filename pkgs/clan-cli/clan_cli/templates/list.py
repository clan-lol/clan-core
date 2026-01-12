from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from clan_lib.templates import list_templates

if TYPE_CHECKING:
    import argparse

    from clan_lib.nix_models.typing import TemplatesClanInput

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    templates = list_templates(args.flake)

    # Display all templates
    for template_type in sorted(templates.builtins):
        builtin_template_set: TemplatesClanInput | None = templates.builtins.get(
            template_type,
            None,
        )  # type: ignore[assignment]
        if not builtin_template_set:
            continue

        print(f"Available '{template_type}' templates")
        print("├── <builtin>")
        for builtin_idx, (name, template) in enumerate(
            sorted(builtin_template_set.items())
        ):
            description = template.get("description", "no description")
            is_last_template = builtin_idx == len(builtin_template_set) - 1
            if not is_last_template:
                print(f"│   ├── {name}: {description}")
            else:
                print(f"│   └── {name}: {description}")

        visible_inputs = sorted(
            (input_name, input_templates)
            for input_name, input_templates in templates.custom.items()
            if template_type in input_templates
        )
        last_idx = len(visible_inputs) - 1
        for input_idx, (input_name, input_templates) in enumerate(visible_inputs):
            custom_templates: TemplatesClanInput = input_templates[template_type]  # type: ignore[literal-required]
            is_last_input = input_idx == last_idx
            prefix = "│" if not is_last_input else " "
            if not is_last_input:
                print(f"├── inputs.{input_name}:")
            else:
                print(f"└── inputs.{input_name}:")

            for custom_idx, (name, template) in enumerate(
                sorted(custom_templates.items())
            ):
                is_last_template = custom_idx == len(custom_templates) - 1
                if not is_last_template:
                    print(
                        f"{prefix}   ├── {name}: {template.get('description', 'no description')}",
                    )
                else:
                    print(
                        f"{prefix}   └── {name}: {template.get('description', 'no description')}",
                    )


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
