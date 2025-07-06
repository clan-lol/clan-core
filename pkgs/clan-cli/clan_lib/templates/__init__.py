import logging
from dataclasses import dataclass

from clan_lib.flake import Flake
from clan_lib.nix_models.clan import ClanTemplatesType

log = logging.getLogger(__name__)


@dataclass
class TemplateList:
    builtins: ClanTemplatesType
    custom: dict[str, ClanTemplatesType]


def list_templates(flake: Flake) -> TemplateList:
    """
    Show information about a module
    """
    custom_templates = flake.select("clanInternals.inventoryClass.templatesPerSource")
    builtin_templates = flake.select("clanInternals.templates")

    return TemplateList(builtin_templates, custom_templates)
