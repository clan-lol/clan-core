import logging
from dataclasses import dataclass

from clan_lib.dirs import clan_templates
from clan_lib.flake import Flake
from clan_lib.nix_models.clan import ClanTemplatesType

log = logging.getLogger(__name__)


@dataclass
class TemplateList:
    builtins: ClanTemplatesType
    custom: dict[str, ClanTemplatesType]


def get_builtin_template_list() -> TemplateList:
    """
    Fallback to get only builtin clan templates with no custom templates.
    """
    builtin_flake = Flake(str(clan_templates()))
    builtin_templates = builtin_flake.select("clanInternals.templates")
    custom_templates: dict[str, ClanTemplatesType] = {}
    return TemplateList(builtin_templates, custom_templates)


def list_templates(flake: Flake | None) -> TemplateList:
    """
    Show information about a module
    """
    if flake is None:
        log.debug("No flake provided, falling back to clan-core builtin templates")
        return get_builtin_template_list()

    try:
        custom_templates = flake.select(
            "clanInternals.inventoryClass.templatesPerSource"
        )
        builtin_templates = flake.select("clanInternals.templates")

        return TemplateList(builtin_templates, custom_templates)

    except (AttributeError, KeyError, Exception):
        log.debug(
            "Failed to get templates from clan inputs, "
            "falling back to clan-core builtin templates"
        )
        return get_builtin_template_list()
