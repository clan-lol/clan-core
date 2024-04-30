import argparse
from dataclasses import dataclass

from clan_cli import create_parser


@dataclass
class Option:
    name: str
    description: str
    default: str | None = None
    metavar: str | None = None
    epilog: str | None = None


@dataclass
class Subcommand:
    name: str
    description: str | None = None
    epilog: str | None = None


@dataclass
class Category:
    title: str
    # Flags such as --example, -e
    options: list[Option]
    # Positionals such as 'cmd <example>'
    positionals: list[Option]

    # Subcommands such as clan 'machines'
    # In contrast to an option it is a command that can have further children
    subcommands: list[Subcommand]
    # Description of the command
    description: str | None = None
    # Additional information, typically displayed at the bottom
    epilog: str | None = None
    # What level of depth the category is at (i.e. 'backups list' is 2, 'backups' is 1, 'clan' is 0)
    level: int = 0


def indent_next(text: str, indent_size: int = 4) -> str:
    """
    Indent all lines in a string except the first line.
    This is useful for adding multiline texts a lists in Markdown.
    """
    indent = " " * indent_size
    lines = text.split("\n")
    indented_text = lines[0] + ("\n" + indent).join(lines[1:])
    return indented_text


def indent_all(text: str, indent_size: int = 4) -> str:
    """
    Indent all lines in a string.
    """
    indent = " " * indent_size
    lines = text.split("\n")
    indented_text = indent + ("\n" + indent).join(lines)
    return indented_text


def get_subcommands(
    parser: argparse.ArgumentParser,
    to: list[Category],
    level: int = 0,
    prefix: list[str] = [],
) -> tuple[list[Option], list[Option], list[Subcommand]]:
    """
    Generate Markdown documentation for an argparse.ArgumentParser instance including its subcommands.

    :param parser: The argparse.ArgumentParser instance.
    :param level: Current depth of subcommand.
    :return: Markdown formatted documentation as a string.
    """

    # Document each argument
    # --flake --option --debug, etc.
    flag_options: list[Option] = []
    positional_options: list[Option] = []
    subcommands: list[Subcommand] = []

    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            # Pseudoaction that holds the help message
            continue

        if isinstance(action, argparse._SubParsersAction):
            continue  # Subparsers handled sperately

        option_strings = ", ".join(action.option_strings)
        if option_strings:
            flag_options.append(
                Option(
                    name=option_strings,
                    description=action.help if action.help else "",
                    default=action.default if action.default is not None else "",
                    metavar=f"{action.metavar}" if action.metavar else "",
                )
            )

        if not option_strings:
            # Positional arguments
            positional_options.append(
                Option(
                    name=action.dest,
                    description=action.help if action.help else "",
                    default=action.default if action.default is not None else "",
                    metavar=f"{action.metavar}" if action.metavar else "",
                )
            )

    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subparsers: dict[str, argparse.ArgumentParser] = action.choices

            for name, subparser in subparsers.items():
                parent = " ".join(prefix)

                sub_command = Subcommand(name=name, description=subparser.description)
                subcommands.append(sub_command)

                (_options, _positionals, _subcommands) = get_subcommands(
                    parser=subparser, to=to, level=level + 1, prefix=[*prefix, name]
                )

                to.append(
                    Category(
                        title=f"{parent} {name}",
                        description=subparser.description,
                        epilog=subparser.epilog,
                        level=level,
                        options=_options,
                        positionals=_positionals,
                        subcommands=_subcommands,
                    )
                )

    return (flag_options, positional_options, subcommands)


def collect_commands() -> list[Category]:
    """
    Returns a sorted list of all available commands.

    i.e.
        a...
        backups
        backups create
        backups list
        backups restore
        c...

    Commands are sorted alphabetically and kept in groups.

    """
    parser = create_parser()

    result: list[Category] = []

    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subparsers: dict[str, argparse.ArgumentParser] = action.choices
            for name, subparser in subparsers.items():
                (_options, _positionals, _subcommands) = get_subcommands(
                    subparser, to=result, level=2, prefix=[name]
                )
                result.append(
                    Category(
                        title=name,
                        description=subparser.description,
                        options=_options,
                        positionals=_positionals,
                        subcommands=_subcommands,
                        level=1,
                    )
                )

    def weight_cmd_groups(c: Category) -> tuple[str, int, str]:
        sub = [o for o in result if o.title.startswith(c.title) and o.title != c.title]
        weight = len(c.title.split(" "))
        if sub:
            weight = len(sub[0].title.split(" "))

        # 1. Sort by toplevel name alphabetically
        # 2. sort by custom weight to keep groups together
        # 3. sort by title alphabetically
        return (c.title.split(" ")[0], weight, c.title)

    result = sorted(result, key=weight_cmd_groups)

    # for c in result:
    #     print(c.title)

    return result


if __name__ == "__main__":
    cmds = collect_commands()

    # TODO: proper markdown
    markdown = ""
    for cmd in cmds:
        markdown += f"## {cmd.title}\n\n"
        markdown += f"{cmd.description}\n" if cmd.description else ""
        markdown += f"{cmd.options}\n" if cmd.description else ""
        markdown += f"{cmd.subcommands}\n" if cmd.description else ""
        markdown += f"{cmd.positionals}\n" if cmd.description else ""
        markdown += f"{cmd.epilog}\n" if cmd.description else ""

        break

    print(markdown)
