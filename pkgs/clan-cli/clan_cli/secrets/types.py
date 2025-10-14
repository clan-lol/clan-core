import argparse
import re
from collections.abc import Callable
from pathlib import Path

from clan_lib.errors import ClanError

from .sops import get_public_age_keys

VALID_SECRET_NAME = re.compile(r"^[a-zA-Z0-9._-]+$")
VALID_USER_NAME = re.compile(r"^[a-z_]([a-z0-9_-]{0,31})?$")

# Maximum length for user and group names
MAX_USER_GROUP_NAME_LENGTH = 32


def secret_name_type(arg_value: str) -> str:
    if not VALID_SECRET_NAME.match(arg_value):
        msg = "Invalid character in secret name. Allowed characters are a-z, A-Z, 0-9, ., -, and _"
        raise argparse.ArgumentTypeError(msg)
    return arg_value


def public_or_private_age_key_type(arg_value: str) -> str:
    try:
        is_file = Path(arg_value).is_file()
    except OSError:
        # Handle "File name too long" errors when age keys are passed directly
        is_file = False

    if is_file:
        arg_value = Path(arg_value).read_text().strip()
    elif arg_value.startswith("AGE-PLUGIN-"):
        msg = (
            f"AGE-PLUGIN keys cannot be used directly as they are plugin identifiers, not recipient keys. "
            f"Please provide the corresponding age1 public key instead. Got: '{arg_value}'"
        )
        raise ClanError(msg)

    public_keys = get_public_age_keys(arg_value)

    match len(public_keys):
        case 0:
            msg = f"Please provide an age public key starting with age1 or an age private key starting with AGE-SECRET-KEY- or AGE-PLUGIN-, got: '{arg_value}'"
            raise ClanError(msg)

        case 1:
            return next(iter(public_keys))

        case n:
            msg = f"{n} age keys were provided, please provide only 1: '{arg_value}'"
            raise ClanError(msg)


def group_or_user_name_type(what: str) -> Callable[[str], str]:
    def name_type(arg_value: str) -> str:
        if len(arg_value) > MAX_USER_GROUP_NAME_LENGTH:
            msg = f"{what.capitalize()} name must be less than 32 characters long"
            raise argparse.ArgumentTypeError(msg)
        if not VALID_USER_NAME.match(arg_value):
            msg = f"Invalid character in {what} name. Allowed characters are a-z, 0-9, -, and _. Must start with a letter or _"
            raise argparse.ArgumentTypeError(msg)
        return arg_value

    return name_type


user_name_type = group_or_user_name_type("user")
group_name_type = group_or_user_name_type("group")
