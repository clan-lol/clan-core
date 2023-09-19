from .folders import machine_folder


def machine_has_fact(machine: str, fact: str) -> bool:
    return (machine_folder(machine) / "facts" / fact).exists()


def machine_get_fact(machine: str, fact: str) -> str:
    return (machine_folder(machine) / "facts" / fact).read_text()
