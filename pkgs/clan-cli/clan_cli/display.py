import argparse

# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD_RED = "\033[1;31m"
DIM = "\033[2m"
RESET = "\033[0m"


def colored(text: str, color: str) -> str:
    """Apply ANSI color to text."""
    return f"{color}{text}{RESET}"


def dim(text: str) -> str:
    """Make text dim."""
    return f"{DIM}{text}{RESET}"


def tree_branch(is_last: bool) -> tuple[str, str]:
    """Get tree branch and child prefix for tree display.

    Returns:
        tuple: (branch, child_prefix) where branch is the tree symbol
               and child_prefix is the indentation for children

    """
    branch = "└──" if is_last else "├──"
    prefix = "     " if is_last else "  │  "
    return branch, prefix


def print_tree_header(title: str, filters: str = "") -> None:
    """Print a formatted tree header with optional filter description."""
    header = colored(title, BOLD_RED)
    if filters:
        header += f" {dim(filters)}"
    print(header)


def build_filter_desc(args: argparse.Namespace, filter_attrs: list[str]) -> str:
    """Build a filter description string from command arguments.

    Args:
        args: Command line arguments
        filter_attrs: List of attribute names to check in args

    Returns:
        Formatted filter description like "(user=alice, machine=laptop)"

    """
    filters = []
    for attr in filter_attrs:
        try:
            if hasattr(args, attr) and getattr(args, attr):
                value = getattr(args, attr)
                filters.append(f"{attr}={value}")
        except AttributeError:
            # Skip attributes that don't exist
            continue
    return f"({', '.join(filters)})" if filters else ""
