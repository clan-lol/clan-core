import re

VALID_MACHINE_NAME = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", re.IGNORECASE)
MAX_MACHINE_NAME_LENGTH = 63


def is_valid_machine_name(name: str) -> bool:
    if len(name) > MAX_MACHINE_NAME_LENGTH:
        return False
    return VALID_MACHINE_NAME.match(name) is not None
