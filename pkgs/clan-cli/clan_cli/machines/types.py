import argparse

from clan_lib.machines.machine_name import (
    MAX_MACHINE_NAME_LENGTH,
    is_valid_machine_name,
)


def validate_hostname(hostname: str) -> bool:
    return is_valid_machine_name(hostname)


def machine_name_type(arg_value: str) -> str:
    if len(arg_value) > MAX_MACHINE_NAME_LENGTH:
        msg = (
            f"Machine name must be less than {MAX_MACHINE_NAME_LENGTH} characters long"
        )
        raise argparse.ArgumentTypeError(msg)
    if not is_valid_machine_name(arg_value):
        msg = "Invalid character in machine name. Allowed characters are a-z, 0-9, and -. Must not start or end with a dash"
        raise argparse.ArgumentTypeError(msg)
    return arg_value
