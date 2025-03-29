# DO NOT EDIT THIS FILE MANUALLY. IT IS GENERATED.
# This file was generated by running `pkgs/clan-cli/clan_cli/inventory/update.sh`
#
# ruff: noqa: N815
# ruff: noqa: N806
# ruff: noqa: F401
# fmt: off
from typing import Any, Literal, NotRequired, TypedDict


class MachineDeploy(TypedDict):
    targetHost: NotRequired[str]


class Machine(TypedDict):
    deploy: NotRequired[MachineDeploy]
    description: NotRequired[str]
    icon: NotRequired[str]
    name: NotRequired[str]
    tags: NotRequired[list[str]]


class Meta(TypedDict):
    name: str
    description: NotRequired[str]
    icon: NotRequired[str]

Service = dict[str, Any]


class Inventory(TypedDict):
    machines: NotRequired[dict[str, Machine]]
    meta: NotRequired[Meta]
    modules: NotRequired[dict[str, Any]]
    services: NotRequired[dict[str, Service]]
    tags: NotRequired[dict[str, Any]]
