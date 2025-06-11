import logging
from pathlib import Path
from typing import Protocol

from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


class Flake(Protocol):
    """
    Protocol for a local flake, which has a path attribute.
    Pass clan_lib.flake.Flake or any other object that implements this protocol.
    """

    @property
    def path(self) -> Path: ...


def transform_url(
    template_type: str, identifier: str, local_path: Flake
) -> tuple[str, str]:
    """
    Transform a template flake ref by injecting the context (clan|machine|disko) into the url.
    We do this for shorthand notation of URLs.
    If the attribute selector path is explicitly selecting an attribute, we don't transform it.

    :param template_type: The type of the template (clan, machine, disko)
    :param identifier: The identifier of the template, which can be a flake reference with a fragment.
    :param local_path: The local flake path, which is used to resolve to a local flake reference, i.e. ".#" shorthand.

    Examples:

    1. injects "machine" as context
    clan machines create --template .#new-machine
    or
    clan machines create --template #new-machine
    -> .#clan.templates.machine.new-machine

    2. injects "clan" as context
    clan create --template .#default
    -> .#clan.templates.clan.default

    3. Dont transform explicit paths (e.g. when more than one attribute selector is present)
    clan machines create --template .#clan.templates.machine.new-machine
    -> .#clan.templates.machine.new-machine

    clan machines create --template .#"new.machine"
    -> .#clan.templates.machine."new.machine"

    4. Builtin templates
    clan machines create --template new.machine
    -> clanInternals.templates.machine."new.machine"

    5. Remote templates
    clan machines create --template github:/org/repo#new.machine
    -> clanInternals.templates.machine."new.machine"

    As of URL specification (RFC 3986).
    scheme:[//[user:password@]host[:port]][/path][?query][#fragment]

    We can safely split the URL into a front part and the fragment
    We can then analyze the fragment and inject the context into the path.

    Of there is no fragment and no URL its a builtin template path.
    new-machine -> #clanInternals.templates.machine."new-machine"

    """
    if identifier.count("#") > 1:
        msg = "Invalid template identifier: More than one '#' found. Please use a single '#'"
        raise ClanError(msg)

    [flake_ref, selector] = (
        identifier.split("#", 1) if "#" in identifier else ["", identifier]
    )
    # Substitute the flake reference with the local flake path if it is empty or just a dot.
    # This is required if the command will be executed from a different place, than the local flake root.
    if not flake_ref or flake_ref == ".":
        flake_ref = str(local_path.path)

    if "#" not in identifier:
        # No fragment, so we assume its a builtin template
        return (flake_ref, f'clanInternals.templates.{template_type}."{selector}"')

    # TODO: implement support for quotes in the tail "a.b".c
    # If the tail contains a dot, or is quoted we assume its a path and don't transform it.
    if '"' in selector or "'" in selector:
        log.warning(
            "Quotes in template paths are not yet supported. Please use unquoted paths."
        )
        return (flake_ref, selector)

    if "." in selector:
        return (flake_ref, selector)

    # Tail doesn't contain a dot at this point, so we can inject the context.
    return (flake_ref, f'clan.templates.{template_type}."{selector}"')
