from dataclasses import dataclass


@dataclass
class ExportScope:
    service: str | None
    instance: str | None
    role: str | None
    machine: str | None


def parse_export(exports_key: str) -> ExportScope:
    [service, instance, role, machine] = exports_key.split(":")
    return ExportScope(service or None, instance or None, role or None, machine or None)
