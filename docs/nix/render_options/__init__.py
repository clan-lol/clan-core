"""Module for rendering NixOS options documentation from JSON format."""

# Options are available in the following format:
# https://github.com/nixos/nixpkgs/blob/master/nixos/lib/make-options-doc/default.nix
#
# ```json
# {
# ...
# "fileSystems.<name>.options": {
#     "declarations": ["nixos/modules/tasks/filesystems.nix"],
#     "default": {
#       "_type": "literalExpression",
#       "text": "[\n  \"defaults\"\n]"
#     },
#     "description": "Options used to mount the file system.",
#     "example": {
#       "_type": "literalExpression",
#       "text": "[\n  \"data=journal\"\n]"
#     },
#     "loc": ["fileSystems", "<name>", "options"],
#     "readOnly": false,
#     "type": "non-empty (list of string (with check: non-empty))"
#     "relatedPackages": "- [`pkgs.tmux`](\n    https://search.nixos.org/packages?show=tmux&sort=relevance&query=tmux\n  )\n",
# }
# }
# ```

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from clan_lib.errors import ClanError
from clan_lib.services.modules import (
    CategoryInfo,
    ModuleManifest,
)

# Get environment variables
CLAN_CORE_PATH = Path(os.environ["CLAN_CORE_PATH"])
CLAN_CORE_DOCS = Path(os.environ["CLAN_CORE_DOCS"])
BUILD_CLAN_PATH = os.environ.get("BUILD_CLAN_PATH")

# Options how to author clan.modules
# perInstance, perMachine, ...
CLAN_SERVICE_INTERFACE = os.environ.get("CLAN_SERVICE_INTERFACE")

CLAN_MODULES_VIA_SERVICE = os.environ.get("CLAN_MODULES_VIA_SERVICE")

OUT = os.environ.get("out")


def sanitize(text: str) -> str:
    return text.replace(">", "\\>")


def replace_git_url(text: str) -> tuple[str, str]:
    res = text
    name = Path(res).name
    if text.startswith("https://git.clan.lol/clan/clan-core/src/branch/main/"):
        name = str(Path(*Path(text).parts[7:]))
    return (res, name)


def render_option_header(name: str) -> str:
    return f"# {name}\n"


def join_lines_with_indentation(lines: list[str], indent: int = 4) -> str:
    """Joins multiple lines with a specified number of whitespace characters as indentation.

    Args:
    lines (list of str): The lines of text to join.
    indent (int): The number of whitespace characters to use as indentation for each line.

    Returns:
    str: The indented and concatenated string.

    """
    # Create the indentation string (e.g., four spaces)
    indent_str = " " * indent
    # Join each line with the indentation added at the beginning
    return "\n".join(indent_str + line for line in lines)


def sanitize_anchor(text: str) -> str:
    parts = text.split(".")
    res = []
    for part in parts:
        if "<" in part:
            continue
        res.append(part)

    return ".".join(res)


def render_option(
    name: str,
    option: dict[str, Any],
    level: int = 3,
    short_head: str | None = None,
) -> str:
    read_only = option.get("readOnly")

    res = f"""
{"#" * level} {sanitize(name) if short_head is None else sanitize(short_head)} {"{: #" + sanitize_anchor(name) + "}" if level > 1 else ""}

"""

    res += f"""
{f"**Attribute: `{name}`**" if short_head is not None else ""}

{"**Readonly**" if read_only else ""}

{option.get("description", "")}
"""
    if option.get("type"):
        res += f"""

**Type**: `{option["type"]}`

"""
    if option.get("default"):
        res += f"""
**Default**:

```nix
{option.get("default", {}).get("text") if option.get("default") else "No default set."}
```
        """
    example = option.get("example", {}).get("text")
    if example:
        example_indented = join_lines_with_indentation(example.split("\n"))
        res += f"""

???+ example

    ```nix
{example_indented}
    ```
"""
    if option.get("relatedPackages"):
        res += f"""
### Related Packages

{option["relatedPackages"]}
"""

    decls = option.get("declarations", [])
    if decls:
        source_path, name = replace_git_url(decls[0])

        name = name.split(",")[0]
        source_path = source_path.split(",")[0]

        res += f"""
:simple-git: Declared in: [{name}]({source_path})
"""
        res += "\n\n"

    return res


def print_options(
    options_file: str,
    head: str,
    no_options: str,
    replace_prefix: str | None = None,
) -> str:
    res = ""
    with (Path(options_file) / "share/doc/nixos/options.json").open() as f:
        options: dict[str, dict[str, Any]] = json.load(f)

        res += head if len(options.items()) else no_options
        for option_name, info in options.items():
            if replace_prefix:
                display_name = option_name.replace(replace_prefix + ".", "")
            else:
                display_name = option_name

            res += render_option(display_name, info, 4)
    return res


def module_header(module_name: str) -> str:
    return f"# {module_name}\n\n"


clan_core_descr = """
`clan.core` is always present in a clan machine

* It is a module of class **`nixos`**
* Provides a set of common options for every machine (in addition to the NixOS options)

Your can customize your machines behavior with the configuration [options](#module-options) provided below.
"""

options_head = """
### Module Options

The following options are available for this module.
"""


def produce_clan_core_docs() -> None:
    if not CLAN_CORE_DOCS:
        msg = f"Environment variables are not set correctly: $CLAN_CORE_DOCS={CLAN_CORE_DOCS}"
        raise ClanError(msg)

    if not OUT:
        msg = f"Environment variables are not set correctly: $out={OUT}"
        raise ClanError(msg)

    # A mapping of output file to content
    core_outputs: dict[str, str] = {}
    with CLAN_CORE_DOCS.open() as f:
        options: dict[str, dict[str, Any]] = json.load(f)
        module_name = "clan.core"

        transform = {n.replace("clan.core.", ""): v for n, v in options.items()}
        split = split_options_by_root(transform)

        # Prepopulate the index file header
        indexfile = f"{module_name}/index.md"
        core_outputs[indexfile] = module_header(module_name) + clan_core_descr

        core_outputs[indexfile] += """!!! info "Submodules"\n"""

        for submodule_name, split_options in split.items():
            root = options_to_tree(split_options)
            module = root.suboptions[0]
            module_type = module.info.get("type")
            if module_type is not None and "submodule" not in module_type:
                continue
            core_outputs[indexfile] += (
                f"      - [{submodule_name}](./{submodule_name}.md)\n"
            )

        core_outputs[indexfile] += options_head

        for submodule_name, split_options in split.items():
            outfile = f"{module_name}/{submodule_name}.md"
            print(
                f"[clan_core.{submodule_name}] Rendering option of: {submodule_name}... {outfile}",
            )
            init_level = 1
            root = options_to_tree(split_options, debug=True)

            print(f"Submodule {submodule_name} - suboptions", len(root.suboptions))

            module = root.suboptions[0]
            print("type", module.info.get("type"))

            module_type = module.info.get("type")
            if module_type is not None and "submodule" not in module_type:
                outfile = indexfile
                init_level = 2

            output = ""
            for option in root.suboptions:
                output += options_docs_from_tree(
                    option,
                    init_level=init_level,
                    prefix=["clan", "core"],
                )

            # Append the content
            if outfile not in core_outputs:
                core_outputs[outfile] = output
            else:
                core_outputs[outfile] += output

        for outfile, output in core_outputs.items():
            (Path(OUT) / outfile).parent.mkdir(parents=True, exist_ok=True)
            with (Path(OUT) / outfile).open("w") as of:
                of.write(output)


def render_categories(
    categories: list[str],
    categories_info: dict[str, CategoryInfo],
) -> str:
    res = """<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">"""
    for cat in categories:
        color = categories_info[cat]["color"]
        res += f"""
    <div style="background-color: {color}; color: white; padding: 10px; border-radius: 20px; text-align: center;">
        {cat}
    </div>
"""
    res += "</div>"
    return res


def produce_clan_service_docs() -> None:
    if not CLAN_MODULES_VIA_SERVICE:
        msg = f"Environment variables are not set correctly: $CLAN_MODULES_VIA_SERVICE={CLAN_MODULES_VIA_SERVICE}"
        raise ClanError(msg)

    if not CLAN_CORE_PATH:
        msg = f"Environment variables are not set correctly: $CLAN_CORE_PATH={CLAN_CORE_PATH}"
        raise ClanError(msg)

    if not OUT:
        msg = f"Environment variables are not set correctly: $out={OUT}"
        raise ClanError(msg)

    indexfile = Path(OUT) / "clanServices/index.md"
    indexfile.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    index = "# Clan Services\n\n"
    index += """
**`clanServices`** are modular building blocks that simplify the configuration and orchestration of multi-host services.

Each `clanService`:

* Is a module of class **`clan.service`**
* Can define **roles** (e.g., `client`, `server`)
* Uses **`inventory.instances`** to configure where and how it is deployed

!!! Note
    `clanServices` are part of Clan's next-generation service model and are intended to replace `clanModules`.

    See [Migration Guide](../../guides/migrations/migrate-inventory-services.md) for help on migrating.

Learn how to use `clanServices` in practice in the [Using clanServices guide](../../guides/clanServices.md).
"""

    with indexfile.open("w") as of:
        of.write(index)

    with Path(CLAN_MODULES_VIA_SERVICE).open() as f3:
        service_links: dict[str, dict[str, dict[str, Any]]] = json.load(f3)

    for module_name, module_info in service_links.items():
        # Skip specific modules that are not ready for documentation
        if module_name in ["internet", "tor"]:
            continue

        output = f"# {module_name}\n\n"
        # output += f"`clan.modules.{module_name}`\n"
        output += f"*{module_info['manifest']['description']}*\n"

        # output += "## Categories\n\n"
        output += render_categories(
            module_info["manifest"]["categories"],
            ModuleManifest.categories_info(),
        )

        output += f"{module_info['manifest']['readme']}\n"

        output += "\n---\n\n## Roles\n"

        output += f"The {module_name} module has the following roles:\n\n"

        for role_name in module_info["roles"]:
            output += f"- {role_name}\n"

        for role_name, role_filename in module_info["roles"].items():
            output += print_options(
                role_filename,
                f"## Options for the `{role_name}` role",
                "This role has no configuration",
                replace_prefix=f"clan.{module_name}",
            )

        outfile = Path(OUT) / f"clanServices/{module_name}.md"
        outfile.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        with outfile.open("w") as of:
            of.write(output)


def split_options_by_root(options: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Split the flat dictionary of options into a dict of which each entry will construct complete option trees.
    {
        "a": { Data }
        "a.b": { Data }
        "c": { Data }
    }
    ->
    {
        "a": {
            "a": { Data },
            "a.b": { Data }
        }
        "c": {
            "c": { Data }
        }
    }
    """
    res: dict[str, dict[str, Any]] = {}
    for key, value in options.items():
        parts = key.split(".")
        root = parts[0]
        if root not in res:
            res[root] = {}
        res[root][key] = value
    return res


def produce_clan_service_author_docs() -> None:
    if not CLAN_SERVICE_INTERFACE:
        msg = f"Environment variables are not set correctly: CLAN_SERVICE_INTERFACE={CLAN_SERVICE_INTERFACE}. Expected a path to the optionsJSON"
        raise ClanError(msg)

    if not OUT:
        msg = f"Environment variables are not set correctly: $out={OUT}"
        raise ClanError(msg)

    output = """
This document describes the structure and configurable attributes of a `clan.service` module.

Typically needed by module authors to define roles, behavior and metadata for distributed services.

!!! Note
    This is not a user-facing documentation, but rather meant as a reference for *module authors*

    See: [clanService Authoring Guide](../../guides/services/community.md)
"""
    # Inventory options are already included under the clan attribute
    # We just omitted them in the clan docs, because we want a separate output for the inventory model
    with Path(CLAN_SERVICE_INTERFACE).open() as f:
        options: dict[str, dict[str, Any]] = json.load(f)

        options_tree = options_to_tree(options, debug=True)
        # Find the inventory options

        # Render the inventory options
        # This for loop excludes the root node
        # for option in options_tree.suboptions:
        output += options_docs_from_tree(options_tree, init_level=2)

    outfile = Path(OUT) / "clanServices/clan-service-author-interface.md"
    outfile.parent.mkdir(parents=True, exist_ok=True)
    with Path.open(outfile, "w") as of:
        of.write(output)


@dataclass
class Option:
    name: str
    path: list[str]
    info: dict[str, Any]
    suboptions: list["Option"] = field(default_factory=list)


def option_short_name(option_name: str) -> str:
    parts = option_name.split(".")
    short_name = ""
    for part in parts[1:]:
        if "<" in part:
            continue
        short_name += ("." + part) if short_name else part
    return short_name


def options_to_tree(options: dict[str, Any], debug: bool = False) -> Option:
    """Convert the options dictionary to a tree structure."""

    # Helper function to create nested structure
    def add_to_tree(path_parts: list[str], info: Any, current_node: Option) -> None:
        if not path_parts:
            return

        name = path_parts[0]
        remaining_path = path_parts[1:]

        # Look for an existing suboption
        for sub in current_node.suboptions:
            if sub.name == name:
                add_to_tree(remaining_path, info, sub)
                return

        # If no existing suboption is found, create a new one
        new_option = Option(
            name=name,
            path=[*current_node.path, name],
            info={},  # Populate info only at the final leaf
        )
        current_node.suboptions.append(new_option)

        # If it's a leaf node, populate info
        if not remaining_path:
            new_option.info = info
        else:
            add_to_tree(remaining_path, info, new_option)

    # Create the root option
    root = Option(name="<root>", path=[], info={})

    # Process each key-value pair in the dictionary
    for key, value in options.items():
        path_parts = key.split(".")
        add_to_tree(path_parts, value, root)

    def print_tree(option: Option, level: int = 0) -> None:
        print("  " * level + option.name + ":", option.path)
        for sub in option.suboptions:
            print_tree(sub, level + 1)

    # Example usage
    if debug:
        print("Options tree:")
        print_tree(root)

    return root


def options_docs_from_tree(
    root: Option,
    init_level: int = 1,
    prefix: list[str] | None = None,
) -> str:
    """Eender the options from the tree structure.

    Args:
    root (Option): The root option node.
    init_level (int): The initial level of indentation.
    prefix (list str): Will be printed as common prefix of all attribute names.

    """

    def render_tree(option: Option, level: int = init_level) -> str:
        output = ""

        should_render = not option.name.startswith("<") and not option.name.startswith(
            "_",
        )
        if should_render:
            # short_name = option_short_name(option.name)
            path = ".".join(prefix + option.path) if prefix else ".".join(option.path)
            output += render_option(
                path,
                option.info,
                level=level,
                short_head=option.name,
            )

        for sub in option.suboptions:
            h_increment = 1 if should_render else 0

            if "_module" in sub.path:
                continue
            output += render_tree(sub, level + h_increment)

        return output

    md = render_tree(root)
    return md


if __name__ == "__main__":
    produce_clan_core_docs()

    produce_clan_service_author_docs()
    produce_clan_service_docs()
