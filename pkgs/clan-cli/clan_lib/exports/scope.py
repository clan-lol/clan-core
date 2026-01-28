from dataclasses import dataclass


@dataclass
class ExportScope:
    service: str
    instance: str
    role: str
    machine: str


def parse_export(exports_key: str) -> ExportScope:
    [service, instance, role, machine] = exports_key.split(":")
    return ExportScope(service, instance, role, machine)
