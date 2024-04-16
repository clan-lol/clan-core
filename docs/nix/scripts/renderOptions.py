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
from pathlib import Path
from typing import Any

# Get environment variables
CLAN_CORE = os.getenv("CLAN_CORE")
CLAN_MODULES = os.environ.get("CLAN_MODULES")
OUT = os.environ.get("out")


def sanitize(text: str) -> str:
    return text.replace(">", "\\>")


def replace_store_path(text: str) -> Path:
    res = text
    if text.startswith("/nix/store/"):
        res = "https://git.clan.lol/clan/clan-core/src/branch/main/" + str(
            Path(*Path(text).parts[4:])
        )
    return Path(res)


def render_option(name: str, option: dict[str, Any]) -> str:
    read_only = option.get("readOnly")

    res = f"""
## {sanitize(name)}
{"Readonly" if read_only else ""}
{option.get("description", "No description available.")}

**Type**: `{option["type"]}`

"""
    if option.get("default"):
        res += f"""
**Default**:

```nix
{option["default"]["text"] if option.get("default") else "No default set."}
```
        """
    example = option.get("example", {}).get("text")
    if example:
        res += f"""

??? example

    ```nix  
    {example}
    ```
"""
    if option.get("relatedPackages"):
        res += f"""
### Related Packages

{option["relatedPackages"]}
"""

    decls = option.get("declarations", [])
    source_path = replace_store_path(decls[0])
    res += f"""
:simple-git: [{source_path.name}]({source_path})
"""
    res += "\n"

    return res


def module_header(module_name: str) -> str:
    return f"""# {module_name}
 
To use this module, import it like this:

```nix
  {{config, lib, inputs, ...}}: {{
    imports = [ inputs.clan-core.clanModules.{module_name} ];
    # ...
  }}
```
"""


def produce_clan_core_docs() -> None:
    if not CLAN_CORE:
        raise ValueError(
            f"Environment variables are not set correctly: $CLAN_CORE={CLAN_CORE}"
        )

    if not OUT:
        raise ValueError(f"Environment variables are not set correctly: $out={OUT}")

    with open(CLAN_CORE) as f:
        options: dict[str, dict[str, Any]] = json.load(f)
        module_name = "clan-core"
        output = module_header(module_name)
        for option_name, info in options.items():
            output += render_option(option_name, info)

        outfile = Path(OUT) / f"{module_name}.md"
        with open(outfile, "w") as of:
            of.write(output)


def produce_clan_modules_docs() -> None:
    if not CLAN_MODULES:
        raise ValueError(
            f"Environment variables are not set correctly: $CLAN_MODULES={CLAN_MODULES}"
        )

    if not OUT:
        raise ValueError(f"Environment variables are not set correctly: $out={OUT}")

    with open(CLAN_MODULES) as f:
        links: dict[str, str] = json.load(f)

    # {'borgbackup': '/nix/store/hi17dwgy7963ddd4ijh81fv0c9sbh8sw-options.json', ... }
    for module_name, options_file in links.items():
        with open(Path(options_file) / "share/doc/nixos/options.json") as f:
            options: dict[str, dict[str, Any]] = json.load(f)
            print(f"Rendering options for {module_name}...")
            output = module_header(module_name)
            for option_name, info in options.items():
                output += render_option(option_name, info)

            outfile = Path(OUT) / f"{module_name}.md"
            with open(outfile, "w") as of:
                of.write(output)


if __name__ == "__main__":
    produce_clan_core_docs()
    produce_clan_modules_docs()
