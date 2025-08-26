import argparse
import re

VALID_HOSTNAME = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", re.IGNORECASE)

# Maximum hostname/machine name length as per RFC specifications
MAX_HOSTNAME_LENGTH = 63


def validate_hostname(hostname: str) -> bool:
    if len(hostname) > MAX_HOSTNAME_LENGTH:
        return False
    return VALID_HOSTNAME.match(hostname) is not None


def machine_name_type(arg_value: str) -> str:
    if len(arg_value) > MAX_HOSTNAME_LENGTH:
        msg = "Machine name must be less than 63 characters long"
        raise argparse.ArgumentTypeError(msg)
    if not VALID_HOSTNAME.match(arg_value):
        msg = "Invalid character in machine name. Allowed characters are a-z, 0-9, ., and -. Must not start with a number"
        raise argparse.ArgumentTypeError(msg)
    return arg_value
