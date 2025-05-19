import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, NewType, TypedDict, cast

from clan_lib.cmd import run
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.flake import Flake

from clan_cli.dirs import clan_templates

log = logging.getLogger(__name__)


InputName = NewType("InputName", str)


@dataclass
class InputVariant:
    input_name: InputName | None

    def is_self(self) -> bool:
        return self.input_name is None

    def __str__(self) -> str:
        return self.input_name or "self"


TemplateName = NewType("TemplateName", str)
TemplateType = Literal["clan", "disko", "machine"]


class Template(TypedDict):
    description: str


class TemplatePath(Template):
    path: str


@dataclass
class FoundTemplate:
    input_variant: InputVariant
    name: TemplateName
    src: TemplatePath


class TemplateTypeDict(TypedDict):
    disko: dict[TemplateName, TemplatePath]
    clan: dict[TemplateName, TemplatePath]
    machine: dict[TemplateName, TemplatePath]


class ClanAttrset(TypedDict):
    templates: TemplateTypeDict


class ClanExports(TypedDict):
    inputs: dict[InputName, ClanAttrset]
    self: ClanAttrset


def apply_fallback_structure(attrset: dict[str, Any]) -> ClanAttrset:
    """Ensure the attrset has all required fields with defaults when missing."""
    # Deep copy not needed since we're constructing the dict from scratch
    result: dict[str, Any] = {}

    # Ensure templates field exists
    if "templates" not in attrset:
        result["templates"] = {"disko": {}, "clan": {}, "machine": {}}
    else:
        templates = attrset["templates"]
        result["templates"] = {
            "disko": templates.get("disko", {}),
            "clan": templates.get("clan", {}),
            "machine": templates.get("machine", {}),
        }

    return cast(ClanAttrset, result)


def get_clan_nix_attrset(clan_dir: Flake | None = None) -> ClanExports:
    """
    Get the clan nix attrset from a flake, with fallback structure applied.
    Path inside the attrsets have NOT YET been realized in the nix store.
    """
    if not clan_dir:
        clan_dir = Flake(str(clan_templates()))

    log.debug(f"Evaluating flake {clan_dir} for Clan attrsets")

    raw_clan_exports: dict[str, Any] = {"self": {"clan": {}}, "inputs": {"clan": {}}}

    maybe_templates = clan_dir.select("?clan.?templates")
    if "clan" in maybe_templates:
        raw_clan_exports["self"] = maybe_templates["clan"]
    else:
        log.info("Current flake does not export the 'clan' attribute")

    # FIXME: flake.select destroys lazy evaluation
    # this is why if one input has a template with a non existant path
    # the whole evaluation will fail
    try:
        # FIXME: We expect here that if the input exports the clan attribute it also has clan.templates
        # this is not always the case if we just want to export clan.modules for example
        # However, there is no way to fix this, as clan.select does not support two optional selectors
        # and we cannot eval the clan attribute as clan.modules can be non JSON serializable because
        # of import statements.
        # This needs to be fixed in clan.select
        # For now always define clan.templates or no clan attribute at all
        temp = clan_dir.select("inputs.*.?clan.templates")

        # FIXME: We need this because clan.select removes the templates attribute
        # but not the clan and other attributes leading up to templates
        for input_name, attrset in temp.items():
            if "clan" in attrset:
                raw_clan_exports["inputs"][input_name] = {
                    "clan": {"templates": {**attrset["clan"]}}
                }

    except ClanCmdError as e:
        msg = "Failed to evaluate flake inputs"
        raise ClanError(msg) from e

    inputs_with_fallback = {}
    for input_name, attrset in raw_clan_exports["inputs"].items():
        # FIXME: flake.select("inputs.*.{clan}") returns the wrong attrset
        # depth when used with conditional fields
        # this is why we have to do a attrset.get here
        inputs_with_fallback[input_name] = apply_fallback_structure(
            attrset.get("clan", {})
        )

    # Apply fallback structure to self
    self_with_fallback = apply_fallback_structure(raw_clan_exports["self"])

    # Construct the final result
    clan_exports: ClanExports = {
        "inputs": inputs_with_fallback,
        "self": self_with_fallback,
    }

    return clan_exports


@dataclass
class InputPrio:
    """
    Strategy for prioritizing inputs when searching for a template
    """

    input_names: tuple[str, ...]  # Tuple of input names (ordered priority list)
    prioritize_self: bool = True  # Whether to prioritize "self" first

    @staticmethod
    def self_only() -> "InputPrio":
        # Only consider "self" (no external inputs)
        return InputPrio(prioritize_self=True, input_names=())

    @staticmethod
    def try_inputs(input_names: tuple[str, ...]) -> "InputPrio":
        # Only consider the specified external inputs
        return InputPrio(prioritize_self=False, input_names=input_names)

    @staticmethod
    def try_self_then_inputs(input_names: tuple[str, ...]) -> "InputPrio":
        # Consider "self" first, then the specified external inputs
        return InputPrio(prioritize_self=True, input_names=input_names)


def copy_from_nixstore(src: Path, dest: Path) -> None:
    run(["cp", "-r", str(src), str(dest)])
    run(["chmod", "-R", "u+w", str(dest)])


@dataclass
class TemplateList:
    inputs: dict[InputName, dict[TemplateName, Template]] = field(default_factory=dict)
    self: dict[TemplateName, Template] = field(default_factory=dict)


def list_templates(
    template_type: TemplateType, clan_dir: Flake | None = None
) -> TemplateList:
    """
    List all templates of a specific type from a flake, without a path attribute.
    As these paths are not yet downloaded into the nix store, and thus cannot be used directly.
    """
    clan_exports = get_clan_nix_attrset(clan_dir)
    result = TemplateList()

    for template_name, template in clan_exports["self"]["templates"][
        template_type
    ].items():
        result.self[template_name] = template

    for input_name, attrset in clan_exports["inputs"].items():
        for template_name, template in attrset["templates"][template_type].items():
            if input_name not in result.inputs:
                result.inputs[input_name] = {}
            result.inputs[input_name][template_name] = template

    return result


def realize_nix_path(clan_dir: Flake, nix_path: str) -> None:
    """
    Downloads / realizes a nix path into the nix store
    """

    if Path(nix_path).exists():
        return

    flake = Flake(identifier=nix_path, inputs_from=clan_dir.identifier)
    flake.invalidate_cache()


def get_template(
    template_name: TemplateName,
    template_type: TemplateType,
    *,
    input_prio: InputPrio | None = None,
    clan_dir: Flake | None = None,
) -> FoundTemplate:
    """
    Find a specific template by name and type within a flake and then ensures it is realized in the nix store.
    """

    if not clan_dir:
        clan_dir = Flake(str(clan_templates()))

    log.info(f"Get template in {clan_dir}")

    log.info(f"Searching for template '{template_name}' of type '{template_type}'")

    # Set default priority strategy if none is provided
    if input_prio is None:
        input_prio = InputPrio.try_self_then_inputs(("clan-core",))

    # Helper function to search for a specific template within a dictionary of templates
    def find_template(
        template_name: TemplateName, templates: dict[TemplateName, TemplatePath]
    ) -> TemplatePath | None:
        if template_name in templates:
            return templates[template_name]
        return None

    # Initialize variables for the search results
    template: TemplatePath | None = None
    input_name: InputName | None = None
    clan_exports = get_clan_nix_attrset(clan_dir)

    # Step 1: Check "self" first, if prioritize_self is enabled
    if input_prio.prioritize_self:
        log.info(f"Checking 'self' for template '{template_name}'")
        template = find_template(
            template_name, clan_exports["self"]["templates"][template_type]
        )

    # Step 2: Otherwise, check the external inputs if no match is found
    if not template and input_prio.input_names:
        log.info(f"Checking external inputs for template '{template_name}'")
        for input_name_str in input_prio.input_names:
            input_name = InputName(input_name_str)
            log.debug(f"Searching in '{input_name}' for template '{template_name}'")

            if input_name not in clan_exports["inputs"]:
                log.debug(f"Skipping input '{input_name}', not found in '{clan_dir}'")
                continue

            template = find_template(
                template_name,
                clan_exports["inputs"][input_name]["templates"][template_type],
            )
            if template:
                log.debug(f"Found template '{template_name}' in input '{input_name}'")
                break

    # Step 3: Raise an error if the template wasn't found
    if not template:
        msg = f"Template '{template_name}' could not be found in '{clan_dir}'"
        raise ClanError(msg)

    realize_nix_path(clan_dir, template["path"])

    return FoundTemplate(
        input_variant=InputVariant(input_name), src=template, name=template_name
    )
