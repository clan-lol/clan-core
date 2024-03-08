# !/usr/bin/env python3
# A subcommand that interfaces with openai to generate nixos configurations and launches VMs with them.
# The `clan clana` command allows the user to enter a prompt with the wishes for the VM and then generates a nixos configuration and launches a VM with it.
# for now this POC should be stateless. A configuration.nix should be generated ina  temporary directory and directly launched.
# there should be no additional arguments.
# THe prompt is read from stdin

import argparse
import os
from pathlib import Path

from clan_cli import clan_openai
from clan_cli.errors import ClanCmdError
from clan_cli.vms.run import run_command

base_config = Path(__file__).parent.joinpath("base-config.nix").read_text()

system_msg = f"""
    Your name is clana, an assistant for creating NixOS configurations.
    Your task is to generate a NixOS configuration.nix file.
    Do not output any explanations or comments, not even when the user asks a question or provides feedback.
    Always provide only the content of the configuration.nix file.
    Don't use any nixos options for which you are not sure about their syntax.
    Generate a configuration.nix which has a very high probability of just working.
    The user who provides the prompt might have technical expertise, or none at all.
    Even a grandmother who has no idea about computers should be able to use this.
    Translate the users requirements to a working configuration.nix file.
    Don't set any options under `nix.`.
    The user should not have a password and log in automatically.

    Take care specifically about:
    - specify every option only once within the same file. Otherwise it will lead to an error like this: error: attribute 'environment.systemPackages' already defined at [...]/configuration.nix:X:X
    - don't set a password for the user. it's already set in the base config


    Assume the following base config is already imported. Any option set in there is already configured and doesn't need to be specified anymore:

    ```nix
    {base_config}
    ```

    The base config will be imported by the system. No need to import it anymore.
"""


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--show", action="store_true", help="show the configuration")
    parser.set_defaults(func=clana_command)


def clana_command(args: argparse.Namespace) -> None:
    print("Please enter your wishes for the new computer: ")
    prompt = input()
    # prompt = "I want to email my grandchildren and watch them on facebook"
    print("Thank you. Generating your computer...")
    # config = clan_openai.complete(messages, model="gpt-4-turbo-preview").strip()
    config = Path(".direnv/configuration.nix").read_text()
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt},
    ]
    conf_dir = Path("/tmp/clana")
    conf_dir.mkdir(exist_ok=True)
    for f in conf_dir.iterdir():
        f.unlink()
    (conf_dir / "flake.nix").write_bytes(
        Path(__file__).parent.joinpath("flake.nix.template").read_bytes()
    )
    with open(conf_dir / "base-config.nix", "w") as f:
        f.write(base_config)
    with open(conf_dir / "hardware-configuration.nix", "w") as f:
        f.write("{}")
    with open(conf_dir / "configuration.nix", "w") as f:
        f.write(
            """
            {
            imports = [
                ./base-config.nix
                ./ai-config.nix
            ];
            }
            """
        )
    while True:
        config_orig = clan_openai.complete(
            messages, model="gpt-4-turbo-preview"
        ).strip()
        # remove code blocks
        lines = config_orig.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:-1]
        config = "\n".join(lines)
        if args.show:
            print("Configuration generated:")
            print(config)
        print("Configuration generated. Launching...")
        with open(conf_dir / "ai-config.nix", "w") as f:
            f.write(config)

        os.environ["NIXPKGS_ALLOW_UNFREE"] = "1"
        try:
            run_command(
                machine="clana-machine", flake=conf_dir, nix_options=["--impure"]
            )
            break
        except ClanCmdError as e:
            messages += [
                {"role": "assistant", "content": config_orig},
                {
                    "role": "system",
                    "content": f"There was a problem that needs to be fixed:\n{e.cmd.stderr}",
                },
            ]
