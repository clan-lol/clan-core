from ..dirs import specific_machine_dir


def machine_has_fact(flake_name: str, machine: str, fact: str) -> bool:
    return (specific_machine_dir(flake_name, machine) / "facts" / fact).exists()


def machine_get_fact(flake_name: str, machine: str, fact: str) -> str:
    return (specific_machine_dir(flake_name, machine) / "facts" / fact).read_text()
