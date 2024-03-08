# Import the urllib.parse, enum and dataclasses modules
import dataclasses
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ClanError


@dataclass
class ClanUrl:
    value: str | Path

    def __str__(self) -> str:
        return (
            f"{self.value}"  # The __str__ method returns a custom string representation
        )

    def __repr__(self) -> str:
        return f"ClanUrl({self.value})"

    def is_local(self) -> bool:
        return isinstance(self.value, Path)

    def is_remote(self) -> bool:
        return isinstance(self.value, str)


# Parameters defined here will be DELETED from the nested uri
# so make sure there are no conflicts with other webservices
@dataclass
class MachineParams:
    dummy_opt: str = "dummy"


@dataclass
class MachineData:
    url: ClanUrl
    name: str = "defaultVM"
    params: MachineParams = dataclasses.field(default_factory=MachineParams)

    def get_id(self) -> str:
        return f"{self.url}#{self.name}"


# Define the ClanURI class
class ClanURI:
    _orig_uri: str
    _components: urllib.parse.ParseResult
    url: ClanUrl
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
        self.url = self._parse_url(clean_comps)

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
            default_machine = MachineData(url=self.url)
            self._machines.append(default_machine)

    def _parse_url(self, comps: urllib.parse.ParseResult) -> ClanUrl:
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
                url = ClanUrl(Path(path).expanduser().resolve())
            case _:
                url = ClanUrl(comps.geturl())

        return url

    def _parse_machine_query(self, machine_frag: str) -> MachineData:
        comp = urllib.parse.urlparse(machine_frag)
        query = urllib.parse.parse_qs(comp.query)
        machine_name = comp.path

        machine_params: dict[str, Any] = {}
        for dfield in dataclasses.fields(MachineParams):
            if dfield.name in query:
                values = query[dfield.name]
                if len(values) > 1:
                    raise ClanError(f"Multiple values for parameter: {dfield.name}")
                machine_params[dfield.name] = values[0]

                # Remove the field from the query dictionary
                # clan uri and nested uri share one namespace for query parameters
                # we need to make sure there are no conflicts
                del query[dfield.name]
        params = MachineParams(**machine_params)
        machine = MachineData(url=self.url, name=machine_name, params=params)
        return machine

    @property
    def machine(self) -> MachineData:
        return self._machines[0]

    def get_orig_uri(self) -> str:
        return self._orig_uri

    def get_url(self) -> str:
        return str(self.url)

    def to_json(self) -> dict[str, Any]:
        return {
            "_orig_uri": self._orig_uri,
            "url": str(self.url),
            "machines": [dataclasses.asdict(m) for m in self._machines],
        }

    def from_json(self, data: dict[str, Any]) -> None:
        self._orig_uri = data["_orig_uri"]
        self.url = data["url"]
        self._machines = [MachineData(**m) for m in data["machines"]]

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
