import logging

from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


def transform_url(template_type: str, identifier: str) -> tuple[str, str]:
    """
    Transform a template flake ref by injecting the context (clan|machine|disko) into the url.
    We do this for shorthand notation of URLs.
    If the attribute selector path is longer than one, don't transform it.

    Examples:

    # injects "machine" as context
    clan machines create --template .#new-machine
    or
    clan machines create --template #new-machine
    -> .#clan.templates.machine.new-machine

    # injects "clan" as context
    clan create --template .#default
    -> .#clan.templates.clan.default

    # Dont transform explicit paths (e.g. when more than one attribute selector is present)
    clan machines create --template .#clan.templates.machine.new-machine
    -> .#clan.templates.machine.new-machine

    clan machines create --template .#"new.machine"
    -> .#clan.templates.machine."new.machine"

    # Builtin templates
    clan machines create --template new.machine
    -> clanInternals.templates.machine."new.machine"

    # Remote templates
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

    if "#" not in identifier:
        # No fragment, so we assume its a builtin template
        return ("", f'clanInternals.templates.{template_type}."{selector}"')

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
