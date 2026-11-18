import argparse
import os
import sys
from dataclasses import dataclass

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
    "(machines) = where the var will be deployed"
)

# Space between 2 columns.
GAP = "  "


def colored(text: str, fg: AnsiColor) -> str:
    if DISABLE_COLOR:
        return text
    return color(text, fg=fg)


def tree_branch(is_last: bool) -> tuple[str, str]:
    """Return the branch symbol of an entry and the prefix for its children."""
    if is_last:
        return "└── ", "    "
    return "├── ", "│   "


@dataclass
class VarRow:
    """A var in the tree, before its columns are padded.

    `own_machine` says that the var sits under the only machine it can be
    deployed to. Then the deployment is left out, because the tree shows it.
    """

    prefix: str
    var: Var
    own_machine: bool

    @property
    def name_cell(self) -> str:
        """Tree prefix, glyph and name, without padding."""
        glyph = SECRET_GLYPH if self.var.secret else PUBLIC_GLYPH
        fg = AnsiColor.RED if self.var.secret else AnsiColor.GREEN
        return f"{self.prefix}{colored(glyph, fg)} {self.var.name}"

    @property
    def name_width(self) -> int:
        """Width of `name_cell` on screen. Color codes take no space."""
        return len(self.prefix) + 2 + len(self.var.name)

    @property
    def deploy_cell(self) -> str:
        """Where the var is deployed, empty when the tree already says it."""
        if not self.var.deploy:
            return "no-deploy"
        if self.own_machine or not self.var.machines:
            return ""
        return f"({', '.join(sorted(self.var.machines))})"

    @property
    def state_cell(self) -> str:
        """Whether the var is generated yet."""
        return "" if self.var.exists else "not generated"


# A rendered line is either finished text or a var whose columns still need
# the width of every other var.
Row = str | VarRow


def pad_rows(rows: list[Row]) -> list[str]:
    """Turn rows into lines, with one column position for the whole tree."""
    var_rows = [row for row in rows if isinstance(row, VarRow)]
    name_width = max((row.name_width for row in var_rows), default=0)
    deploy_width = max((len(row.deploy_cell) for row in var_rows), default=0)

    lines = []
    for row in rows:
        if isinstance(row, str):
            lines.append(row)
            continue
        deploy = row.deploy_cell
        padded_deploy = colored(deploy, AnsiColor.YELLOW) if deploy else ""
        padded_deploy += " " * (deploy_width - len(deploy))
        line = (
            row.name_cell
            + " " * (name_width - row.name_width)
            + GAP
            + padded_deploy
            + GAP
            + colored(row.state_cell, AnsiColor.YELLOW)
        )
        lines.append(line.rstrip())
    return lines


def render_vars(generator: Generator, prefix: str, own_machine: bool) -> list[Row]:
    """Render the vars of one generator."""
    rows: list[Row] = []
    files = sorted(generator.files, key=lambda var: var.name)
    for i, var in enumerate(files):
        branch, _ = tree_branch(i == len(files) - 1)
        rows.append(VarRow(prefix=prefix + branch, var=var, own_machine=own_machine))
    return rows


def render_generators(
    generators: list[Generator],
    prefix: str,
    own_machine: bool,
) -> list[Row]:
    """Render generators with their vars below them."""
    rows: list[Row] = []
    ordered = sorted(generators, key=lambda generator: generator.name)
    for i, generator in enumerate(ordered):
        branch, child_prefix = tree_branch(i == len(ordered) - 1)
        rows.append(f"{prefix}{branch}{colored(generator.name, AnsiColor.BLUE)}")
        rows.extend(render_vars(generator, prefix + child_prefix, own_machine))
    return rows


def render_scope(scope: dict[str, list[Generator]], own_machine: bool) -> list[Row]:
    """Render one scope: every machine or export key with its generators."""
    rows: list[Row] = []
    entries = sorted(scope.items())
    for i, (entry, generators) in enumerate(entries):
        branch, child_prefix = tree_branch(i == len(entries) - 1)
        rows.append(f"{branch}{colored(entry, AnsiColor.GREEN)}")
        rows.extend(render_generators(generators, child_prefix, own_machine))
    return rows


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

    rows: list[Row] = [colored(LEGEND, AnsiColor.CYAN)]
    for title, body in blocks:
        rows.append("")
        rows.append(colored(title, AnsiColor.YELLOW))
        rows.extend(body)
    return pad_rows(rows)


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
