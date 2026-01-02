import argparse


class HelpFormatter(argparse.RawTextHelpFormatter):
    """Extend the RawTextHelpFormatter with default display text for enums.

    Example:
     `The type of hardware report to generate. (default: nixos-facter)`

    """

    def _get_help_string(self, action: argparse.Action) -> str:
        help_text = action.help or ""
        if "%(default)" in help_text:
            return help_text
        if not getattr(action, "choices", None):
            return help_text
        if action.default is None:
            return help_text
        return f"{help_text} (default: {action.default})"
