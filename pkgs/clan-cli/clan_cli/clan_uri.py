# Import the urllib.parse, enum and dataclasses modules
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .errors import ClanError


@dataclass
class FlakeId:
    _value: str | Path

    def __str__(self) -> str:
        return f"{self._value}"  # The __str__ method returns a custom string representation

    @property
    def path(self) -> Path:
        assert isinstance(self._value, Path)
        return self._value

    @property
    def url(self) -> str:
        assert isinstance(self._value, str)
        return self._value

    def __repr__(self) -> str:
        return f"ClanUrl({self._value})"

    def is_local(self) -> bool:
        return isinstance(self._value, Path)

    def is_remote(self) -> bool:
        return isinstance(self._value, str)


@dataclass
class MachineData:
    flake_id: FlakeId
    name: str = "defaultVM"

    def get_id(self) -> str:
        return f"{self.flake_id}#{self.name}"


# Define the ClanURI class
class ClanURI:
    _orig_uri: str
    _components: urllib.parse.ParseResult
    flake_id: FlakeId
    _machines: list[MachineData]

    # Initialize the class with a clan:// URI
    def __init__(self, uri: str) -> None:
        self._machines = []

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
        self._components = urllib.parse.urlparse(nested_uri)

        # Replace the query string in the components with the new query string
        clean_comps = self._components._replace(
            query=self._components.query, fragment=""
        )

        # Parse the URL into a ClanUrl object
        self.flake_id = self._parse_url(clean_comps)

        # Parse the fragment into a list of machine queries
        # Then parse every machine query into a MachineParameters object
        machine_frags = list(
            filter(lambda x: len(x) > 0, self._components.fragment.split("#"))
        )
        for machine_frag in machine_frags:
            machine = self._parse_machine_query(machine_frag)
            self._machines.append(machine)

        # If there are no machine fragments, add a default machine
        if len(machine_frags) == 0:
            default_machine = MachineData(flake_id=self.flake_id)
            self._machines.append(default_machine)

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

    def _parse_machine_query(self, machine_frag: str) -> MachineData:
        comp = urllib.parse.urlparse(machine_frag)
        machine_name = comp.path

        machine = MachineData(flake_id=self.flake_id, name=machine_name)
        return machine

    @property
    def machine(self) -> MachineData:
        return self._machines[0]

    def get_orig_uri(self) -> str:
        return self._orig_uri

    def get_url(self) -> str:
        return str(self.flake_id)

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

    def __str__(self) -> str:
        return self.get_orig_uri()

    def __repr__(self) -> str:
        return f"ClanURI({self})"
