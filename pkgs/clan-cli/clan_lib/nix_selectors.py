"""Central registry of all Nix attribute selectors used in clan-lib.

IMPORTANT: All code MUST use these selectors instead of inline strings.
Inline selector strings like "clanInternals.machines..." are forbidden.

This ensures:
1. All selectors are tested to exist in Nix
2. Selectors can be mocked in tests
3. API surface is explicit and discoverable
"""

from collections.abc import Callable, Iterable

type StaticSel = Callable[[], str]
type MachineSel = Callable[[str, str], str]
type MachinesSel = Callable[[str, Iterable[str]], str]
type GeneratorSel = Callable[[str, str, str], str]

# Tests registries
# Populated by decorators
# Picked up by unit tests automatically
STATIC_SELECTORS: list[StaticSel] = []
MACHINE_SELECTORS: list[MachineSel] = []
MACHINES_SELECTORS: list[MachinesSel] = []
GENERATOR_SELECTORS: list[GeneratorSel] = []


# Decorator functions
def static_selector[T: StaticSel](func: T) -> T:
    """Register a static selector (no parameters)."""
    STATIC_SELECTORS.append(func)
    return func


def machine_selector[T: MachineSel](func: T) -> T:
    """Register a machine selector (system, machine)."""
    MACHINE_SELECTORS.append(func)
    return func


def machines_selector[T: MachinesSel](func: T) -> T:
    """Register a multi-machine selector (system, machines[])."""
    MACHINES_SELECTORS.append(func)
    return func


def generator_selector[T: GeneratorSel](func: T) -> T:
    """Register a generator selector (system, machine, generator)."""
    GENERATOR_SELECTORS.append(func)
    return func


# STATIC SELECTORS


@static_selector
def source_info() -> str:
    return "sourceInfo"


@static_selector
def secrets_age_plugins() -> str:
    return "clanInternals.?secrets.?age.?plugins"


@static_selector
def inventory_relative_directory() -> str:
    return "clanInternals.inventoryClass.relativeDirectory"


@static_selector
def clan_exports() -> str:
    return "clan.?exports"


# MACHINE SELECTORS (system, machine)


@machine_selector
def deployment_require_explicit_update(system: str, machine: str) -> str:
    return f"clanInternals.machines.{system}.{machine}.config.clan.deployment.requireExplicitUpdate"


@machine_selector
def deployment_nixos_mobile_workaround(system: str, machine: str) -> str:
    return f"clanInternals.machines.{system}.{machine}.config.system.clan.deployment.nixosMobileWorkaround"


# MULTI-MACHINE SELECTORS (system, machines[])


@machines_selector
def vars_generators_metadata(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.generators.*.{{share,dependencies,prompts,validationHash}}"


@machines_selector
def vars_generators_files(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.generators.*.files.*.{{secret,deploy,owner,group,mode,neededFor}}"


@machines_selector
def vars_sops_default_groups(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.?sops.?defaultGroups"


@machines_selector
def vars_settings_public_module(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.settings.publicModule"


@machines_selector
def vars_settings_secret_module(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.settings.secretModule"


@machines_selector
def vars_sops_secret_upload_dir(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.?sops.?secretUploadDirectory"


@machines_selector
def vars_password_store_pass_command(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.?password-store.?passCommand"


@machines_selector
def vars_password_store_secret_location(system: str, machines: Iterable[str]) -> str:
    return f"clanInternals.machines.{system}.{{{','.join(machines)}}}.config.clan.core.vars.?password-store.?secretLocation"


# GENERATOR SELECTORS (system, machine, generator)


@generator_selector
def generator_final_script(system: str, machine: str, generator: str) -> str:
    return f'clanInternals.machines.{system}.{machine}.config.clan.core.vars.generators."{generator}".finalScript'
