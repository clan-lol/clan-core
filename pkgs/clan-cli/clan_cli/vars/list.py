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

# Marks a secret var. A filled circle reads as "closed".
SECRET_GLYPH = "●"  # noqa: S105 - a glyph, not a credential
# Marks a public var. An empty circle reads as "open".
PUBLIC_GLYPH = "○"

LEGEND = (
    f"{SECRET_GLYPH} secret  {PUBLIC_GLYPH} public  "
    "(machines) = where the var is deployed, as declared in the module, "
    "not checked on the machine"
)


def colored(text: str, fg: AnsiColor) -> str:
    if DISABLE_COLOR:
        return text
    return color(text, fg=fg)


def tree_branch(is_last: bool) -> tuple[str, str]:
    """Return the branch symbol of an entry and the prefix for its children."""
    if is_last:
        return "└── ", "    "
    return "├── ", "│   "


def describe_var(var: Var, name_width: int, own_machine: bool) -> str:
    """Return one line that describes a var.

    A var has 3 states that matter: secret or public, deployed or not, and
    generated or not. The value is never printed, use `clan vars get` for it.

    `own_machine` says that the var sits under the only machine it can be
    deployed to. Then the deployment is left out, because the tree shows it.
    Only a var that is not deployed says so.
    """
    glyph = SECRET_GLYPH if var.secret else PUBLIC_GLYPH
    glyph = colored(glyph, AnsiColor.RED if var.secret else AnsiColor.GREEN)
    name = var.name.ljust(name_width)

    if not var.deploy:
        state = colored("no-deploy", AnsiColor.YELLOW)
    elif own_machine or not var.machines:
        state = ""
    else:
        state = f"({', '.join(sorted(var.machines))})"

    if not var.exists:
        not_generated = colored("not generated", AnsiColor.YELLOW)
        state = f"{state}  {not_generated}" if state else not_generated
    return f"{glyph} {name}  {state}".rstrip()


def render_vars(generator: Generator, prefix: str, own_machine: bool) -> list[str]:
    """Render the vars of one generator."""
    lines = []
    files = sorted(generator.files, key=lambda var: var.name)
    name_width = max((len(var.name) for var in files), default=0)
    for i, var in enumerate(files):
        branch, _ = tree_branch(i == len(files) - 1)
        lines.append(f"{prefix}{branch}{describe_var(var, name_width, own_machine)}")
    return lines


def render_generators(
    generators: list[Generator],
    prefix: str,
    own_machine: bool,
) -> list[str]:
    """Render generators with their vars below them."""
    lines = []
    ordered = sorted(generators, key=lambda generator: generator.name)
    for i, generator in enumerate(ordered):
        branch, child_prefix = tree_branch(i == len(ordered) - 1)
        lines.append(f"{prefix}{branch}{colored(generator.name, AnsiColor.BLUE)}")
        lines.extend(render_vars(generator, prefix + child_prefix, own_machine))
    return lines


def render_scope(scope: dict[str, list[Generator]], own_machine: bool) -> list[str]:
    """Render one scope: every machine or export key with its generators."""
    lines = []
    entries = sorted(scope.items())
    for i, (entry, generators) in enumerate(entries):
        branch, child_prefix = tree_branch(i == len(entries) - 1)
        lines.append(f"{branch}{colored(entry, AnsiColor.GREEN)}")
        lines.extend(render_generators(generators, child_prefix, own_machine))
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
        ("Shared", render_generators(shared, "", own_machine=False)),
        # A per-machine var can only be deployed to the machine it sits under
        ("Per-Machine", render_scope(per_machine, own_machine=True)),
        ("Per-Export", render_scope(per_export, own_machine=False)),
    ]
    blocks = [(title, body) for title, body in blocks if body]
    if not blocks:
        return ["No vars found"]

    lines: list[str] = [colored(LEGEND, AnsiColor.CYAN)]
    for title, body in blocks:
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
