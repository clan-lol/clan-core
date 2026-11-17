import argparse
import os
import sys

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.colors import AnsiColor, color
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine
from clan_lib.vars._types import PerExport, PerMachine, Shared
from clan_lib.vars.generator import Generator
from clan_lib.vars.list import get_clan_generators, get_machine_vars
from clan_lib.vars.var import Var

# https://no-color.org
DISABLE_COLOR = not sys.stdout.isatty() or os.environ.get("NO_COLOR", "") != ""

# Longest value printed on one line. A longer value is cut.
MAX_VALUE_WIDTH = 60


def colored(text: str, fg: AnsiColor) -> str:
    if DISABLE_COLOR:
        return text
    return color(text, fg=fg)


def tree_branch(is_last: bool) -> tuple[str, str]:
    """Return the branch symbol of an entry and the prefix for its children."""
    if is_last:
        return "└── ", "    "
    return "├── ", "│   "


def one_line(value: str) -> str:
    """Return `value` as one short line, so that it fits into the tree.

    A generator usually writes a trailing newline. That newline is not content,
    so it never counts as cut.
    """
    text = value.rstrip("\n")
    first_line = text.split("\n", 1)[0]
    cut = len(first_line) < len(text)
    if len(first_line) > MAX_VALUE_WIDTH:
        first_line = first_line[:MAX_VALUE_WIDTH]
        cut = True
    return first_line + "…" if cut else first_line


def describe_var(var: Var) -> str:
    """Return the name of a var and what is known about its content."""
    name = colored(var.name, AnsiColor.RED if var.secret else AnsiColor.MAGENTA)
    if not var.exists:
        return f"{name} <not set>"
    if not var.secret:
        return f"{name} {one_line(var.printable_value)}"
    if not var.deploy:
        return f"{name} {colored('not deployed', AnsiColor.CYAN)}"
    receivers = ", ".join(sorted(var.machines))
    return f"{name} {colored(f'→ {receivers}', AnsiColor.CYAN)}"


def render_vars(generator: Generator, prefix: str) -> list[str]:
    """Render the vars of one generator."""
    lines = []
    files = sorted(generator.files, key=lambda var: var.name)
    for i, var in enumerate(files):
        branch, _ = tree_branch(i == len(files) - 1)
        lines.append(f"{prefix}{branch}{describe_var(var)}")
    return lines


def render_generators(generators: list[Generator], prefix: str) -> list[str]:
    """Render generators with their vars below them."""
    lines = []
    ordered = sorted(generators, key=lambda generator: generator.name)
    for i, generator in enumerate(ordered):
        branch, child_prefix = tree_branch(i == len(ordered) - 1)
        lines.append(f"{prefix}{branch}{colored(generator.name, AnsiColor.BLUE)}")
        lines.extend(render_vars(generator, prefix + child_prefix))
    return lines


def render_scope(scope: dict[str, list[Generator]]) -> list[str]:
    """Render one scope: every machine or export key with its generators."""
    lines = []
    entries = sorted(scope.items())
    for i, (entry, generators) in enumerate(entries):
        branch, child_prefix = tree_branch(i == len(entries) - 1)
        lines.append(f"{branch}{colored(entry, AnsiColor.GREEN)}")
        lines.extend(render_generators(generators, child_prefix))
    return lines


def render_clan_vars(generators: list[Generator]) -> list[str]:
    """Render all vars of a clan as a tree, grouped by placement."""
    shared: list[Generator] = []
    per_machine: dict[str, list[Generator]] = {}
    per_export: dict[str, list[Generator]] = {}

    for generator in generators:
        placement = generator.key.placement
        if isinstance(placement, Shared):
            shared.append(generator)
        elif isinstance(placement, PerMachine):
            per_machine.setdefault(placement.machine, []).append(generator)
        elif isinstance(placement, PerExport):
            per_export.setdefault(placement.exports_key, []).append(generator)

    blocks = [
        ("Shared", render_generators(shared, "")),
        ("Per-Machine", render_scope(per_machine)),
        ("Per-Export", render_scope(per_export)),
    ]
    blocks = [(title, body) for title, body in blocks if body]
    if not blocks:
        return ["No vars found"]

    lines: list[str] = []
    for i, (title, body) in enumerate(blocks):
        if i:
            lines.append("")
        lines.append(colored(title, AnsiColor.YELLOW))
        lines.extend(body)
    return lines


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    if args.machine is None:
        print("\n".join(render_clan_vars(get_clan_generators(flake))))
        return
    machine = Machine(name=args.machine, flake=flake)
    all_vars = get_machine_vars(machine)
    print("\n".join(sorted(str(var) for var in all_vars)))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    machines_arg = parser.add_argument(
        "machine",
        nargs="?",
        default=None,
        help="The machine to print vars for. Without it, all vars of the clan are printed",
    )
    add_dynamic_completer(machines_arg, complete_machines)

    parser.set_defaults(func=list_command)
