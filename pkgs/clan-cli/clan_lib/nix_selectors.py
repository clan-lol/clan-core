"""Central registry of all Nix attribute selectors used in clan-lib.

IMPORTANT: All code MUST use these selectors instead of inline strings.
Inline selector strings like "clanInternals.machines..." are forbidden.

This ensures:
1. All selectors are tested to exist in Nix
2. Selectors can be mocked in tests
3. API surface is explicit and discoverable
"""

from collections.abc import Callable
from contextvars import ContextVar

# Default prefix for machine selectors
DEFAULT_MACHINE_PREFIX = "clanInternals.machines"

# Context variable for machine selector prefix
# Set this via set_machine_prefix() when working with a specific flake
_machine_prefix: ContextVar[str] = ContextVar(
    "machine_prefix", default=DEFAULT_MACHINE_PREFIX
)


def set_machine_prefix(prefix: str) -> None:
    """Set the machine selector prefix for the current context.

    Call this when you have a custom flake;
    i.e. where machines are exposed in checks.{system}.machinesCross
    """
    _machine_prefix.set(prefix)


def get_machine_prefix() -> str:
    """Get the current machine selector prefix."""
    return _machine_prefix.get()


type StaticSel = Callable[[], str]
type MachineSel = Callable[[str, str], str]  # system, machine
type MachinesSel = Callable[[str, list[str]], str]  # system, machines
type GeneratorSel = Callable[[str, str, str], str]  # system, machine, generator
type ModuleSel = Callable[[str, str], str]  # input, module

# Tests registries
# Populated by decorators
# Picked up by unit tests automatically
STATIC_SELECTORS: list[StaticSel] = []
MACHINE_SELECTORS: list[MachineSel] = []
MACHINES_SELECTORS: list[MachinesSel] = []
GENERATOR_SELECTORS: list[GeneratorSel] = []
MODULE_SELECTORS: list[ModuleSel] = []


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


def module_selector[T: ModuleSel](func: T) -> T:
    """Register a generator selector (system, machine, generator)."""
    MODULE_SELECTORS.append(func)
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


@static_selector
def inventory_input_modules() -> str:
    return "clanInternals.inventoryClass.modulesPerSource"


@static_selector
def inventory_static_modules() -> str:
    return "clanInternals.inventoryClass.staticModules"


## MODULE SELECTORS (input_name, module)


@module_selector
def inventory_module_schema(input_name: str, module: str) -> str:
    return f"clanInternals.inventoryClass.moduleSchemas.{input_name}.{module}"


# MACHINE SELECTORS (system, machine)


# MULTI-MACHINE SELECTORS (system, machines[])


@machines_selector
def vars_generators_metadata(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.generators.*.{{share,dependencies,prompts,validationHash}}"


@machines_selector
def vars_generators_files(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.generators.*.files.*.{{secret,deploy,owner,group,mode,neededFor}}"


@machines_selector
def vars_sops_default_groups(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.?sops.?defaultGroups"


@machines_selector
def vars_settings_public_module(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.settings.publicModule"


@machines_selector
def vars_settings_secret_module(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.settings.secretModule"


@machines_selector
def vars_sops_secret_upload_dir(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.?sops.?secretUploadDirectory"


@machines_selector
def vars_password_store_pass_command(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.?password-store.?passCommand"


@machines_selector
def vars_password_store_secret_location(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.core.vars.?password-store.?secretLocation"


@machines_selector
def deployment_require_explicit_update(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.clan.deployment.requireExplicitUpdate"


@machines_selector
def deployment_nixos_mobile_workaround(system: str, machines: list[str]) -> str:
    prefix = get_machine_prefix()
    return f"{prefix}.{system}.{{{','.join(machines)}}}.config.system.clan.deployment.nixosMobileWorkaround"


# GENERATOR SELECTORS (system, machine, generator)


@generator_selector
def generator_final_script(system: str, machine: str, generator: str) -> str:
    prefix = get_machine_prefix()
    return f'{prefix}.{system}.{machine}.config.clan.core.vars.generators."{generator}".finalScript'
