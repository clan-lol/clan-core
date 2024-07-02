# Import the urllib.parse, enum and dataclasses modules
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .errors import ClanError


@dataclass
class FlakeId:
    # FIXME: this is such a footgun if you accidnetally pass a string
    _value: str | Path

    def __str__(self) -> str:
        return str(
            self._value
        )  # The __str__ method returns a custom string representation

    @property
    def path(self) -> Path:
        assert isinstance(self._value, Path)
        return self._value

    @property
    def url(self) -> str:
        assert isinstance(self._value, str)
        return self._value

    def is_local(self) -> bool:
        return isinstance(self._value, Path)

    def is_remote(self) -> bool:
        return isinstance(self._value, str)


# Define the ClanURI class
@dataclass
class ClanURI:
    flake: FlakeId
    machine_name: str

    # Initialize the class with a clan:// URI
    def __init__(self, uri: str) -> None:
        # users might copy whitespace along with the uri
        uri = uri.strip()
        self._orig_uri = uri

        # Check if the URI starts with clan://
        # If it does, remove the clan:// prefix
        if uri.startswith("clan://"):
            nested_uri = uri[7:]
        else:
            raise ClanError(f"Invalid uri: expected clan://, got {uri}")

        # Parse the URI into components
        # url://netloc/path;parameters?query#fragment
        components: urllib.parse.ParseResult = urllib.parse.urlparse(nested_uri)

        # Replace the query string in the components with the new query string
        clean_comps = components._replace(query=components.query, fragment="")

        # Parse the URL into a ClanUrl object
        self.flake = self._parse_url(clean_comps)
        self.machine_name = "defaultVM"
        if components.fragment:
            self.machine_name = components.fragment

    def _parse_url(self, comps: urllib.parse.ParseResult) -> FlakeId:
        comb = (
            comps.scheme,
            comps.netloc,
            comps.path,
            comps.params,
            comps.query,
            comps.fragment,
        )
        match comb:
            case ("file", "", path, "", "", _) | ("", "", path, "", "", _):  # type: ignore
                flake_id = FlakeId(Path(path).expanduser().resolve())
            case _:
                flake_id = FlakeId(comps.geturl())

        return flake_id

    def get_url(self) -> str:
        return str(self.flake)

    @classmethod
    def from_str(
        cls,  # noqa
        url: str,
        machine_name: str | None = None,
    ) -> "ClanURI":
        clan_uri = ""
        if not url.startswith("clan://"):
            clan_uri += "clan://"

        clan_uri += url

        if machine_name:
            clan_uri += f"#{machine_name}"

        return cls(clan_uri)
