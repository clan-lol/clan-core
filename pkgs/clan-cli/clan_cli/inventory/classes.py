
# DON NOT EDIT THIS FILE MANUALLY. IT IS GENERATED.
# UPDATE
# ruff: noqa: N815
# ruff: noqa: N806
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MachineDeploy:
    targetHost: str | None = None


@dataclass
class Machine:
    deploy: MachineDeploy
    name: str
    description: str | None = None
    icon: str | None = None
    system: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class Meta:
    name: str
    description: str | None = None
    icon: str | None = None


@dataclass
class BorgbackupConfigDestination:
    repo: str
    name: str


@dataclass
class BorgbackupConfig:
    destinations: dict[str, BorgbackupConfigDestination] | dict[str,Any] = field(default_factory=dict)


@dataclass
class ServiceBorgbackupMachine:
    config: BorgbackupConfig | dict[str,Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)


@dataclass
class ServiceBorgbackupMeta:
    name: str
    description: str | None = None
    icon: str | None = None


@dataclass
class ServiceBorgbackupRoleClient:
    config: BorgbackupConfig | dict[str,Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
    machines: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ServiceBorgbackupRoleServer:
    config: BorgbackupConfig | dict[str,Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
    machines: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ServiceBorgbackupRole:
    client: ServiceBorgbackupRoleClient
    server: ServiceBorgbackupRoleServer


@dataclass
class ServiceBorgbackup:
    meta: ServiceBorgbackupMeta
    roles: ServiceBorgbackupRole
    config: BorgbackupConfig | dict[str,Any] = field(default_factory=dict)
    machines: dict[str, ServiceBorgbackupMachine] | dict[str,Any] = field(default_factory=dict)


@dataclass
class PackagesConfig:
    packages: list[str] = field(default_factory=list)


@dataclass
class ServicePackageMachine:
    config: dict[str,Any] | PackagesConfig = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)


@dataclass
class ServicePackageMeta:
    name: str
    description: str | None = None
    icon: str | None = None


@dataclass
class ServicePackageRoleDefault:
    config: dict[str,Any] | PackagesConfig = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
    machines: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ServicePackageRole:
    default: ServicePackageRoleDefault


@dataclass
class ServicePackage:
    meta: ServicePackageMeta
    roles: ServicePackageRole
    config: dict[str,Any] | PackagesConfig = field(default_factory=dict)
    machines: dict[str, ServicePackageMachine] | dict[str,Any] = field(default_factory=dict)


@dataclass
class SingleDiskConfig:
    device: str


@dataclass
class ServiceSingleDiskMachine:
    config: SingleDiskConfig | dict[str,Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)


@dataclass
class ServiceSingleDiskMeta:
    name: str
    description: str | None = None
    icon: str | None = None


@dataclass
class ServiceSingleDiskRoleDefault:
    config: SingleDiskConfig | dict[str,Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
    machines: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ServiceSingleDiskRole:
    default: ServiceSingleDiskRoleDefault


@dataclass
class ServiceSingleDisk:
    meta: ServiceSingleDiskMeta
    roles: ServiceSingleDiskRole
    config: SingleDiskConfig | dict[str,Any] = field(default_factory=dict)
    machines: dict[str, ServiceSingleDiskMachine] | dict[str,Any] = field(default_factory=dict)


@dataclass
class Service:
    borgbackup: dict[str, ServiceBorgbackup] = field(default_factory=dict)
    packages: dict[str, ServicePackage] = field(default_factory=dict)
    single_disk: dict[str, ServiceSingleDisk] = field(default_factory=dict)


@dataclass
class Inventory:
    meta: Meta
    services: Service
    machines: dict[str, Machine] | dict[str,Any] = field(default_factory=dict)
