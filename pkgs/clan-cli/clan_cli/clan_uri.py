# Import the urllib.parse, enum and dataclasses modules
import dataclasses
import urllib.parse
import urllib.request
from dataclasses import dataclass
from enum import Enum, member
from pathlib import Path
from typing import Any, Self

from .errors import ClanError


# Define an enum with different members that have different values
class ClanScheme(Enum):
    # Use the dataclass decorator to add fields and methods to the members
    @member
    @dataclass
    class REMOTE:
        url: str  # The url field holds the HTTP URL

        def __str__(self) -> str:
            return f"REMOTE({self.url})"  # The __str__ method returns a custom string representation

    @member
    @dataclass
    class LOCAL:
        path: Path  # The path field holds the local path

        def __str__(self) -> str:
            return f"LOCAL({self.path})"  # The __str__ method returns a custom string representation


# Parameters defined here will be DELETED from the nested uri
# so make sure there are no conflicts with other webservices
@dataclass
class ClanParameters:
    flake_attr: str = "defaultVM"


# Define the ClanURI class
class ClanURI:
    # Initialize the class with a clan:// URI
    def __init__(self, uri: str) -> None:
        # users might copy whitespace along with the uri
        uri = uri.strip()
        self._full_uri = uri

        # Check if the URI starts with clan://
        # If it does, remove the clan:// prefix
        if uri.startswith("clan://"):
            self._nested_uri = uri[7:]
        else:
            raise ClanError(f"Invalid scheme: expected clan://, got {uri}")

        # Parse the URI into components
        # scheme://netloc/path;parameters?query#fragment
        self._components = urllib.parse.urlparse(self._nested_uri)

        # Parse the query string into a dictionary
        query = urllib.parse.parse_qs(self._components.query)

        # Create a new dictionary with only the parameters we want
        # example: https://example.com?flake_attr=myVM&password=1234
        # becomes: https://example.com?password=1234
        # clan_params = {"flake_attr": "myVM"}
        # query = {"password": ["1234"]}
        clan_params: dict[str, str] = {}
        for field in dataclasses.fields(ClanParameters):
            if field.name in query:
                values = query[field.name]
                if len(values) > 1:
                    raise ClanError(f"Multiple values for parameter: {field.name}")
                clan_params[field.name] = values[0]

                # Remove the field from the query dictionary
                # clan uri and nested uri share one namespace for query parameters
                # we need to make sure there are no conflicts
                del query[field.name]
        # Reencode the query dictionary into a query string
        real_query = urllib.parse.urlencode(query, doseq=True)

        # If the fragment contains a #, use the part after the # as the flake_attr
        # on multiple #, use the first one
        if self._components.fragment != "":
            clan_params["flake_attr"] = self._components.fragment.split("#")[0]

        # Replace the query string in the components with the new query string
        self._components = self._components._replace(query=real_query, fragment="")

        # Create a ClanParameters object from the clan_params dictionary
        self.params = ClanParameters(**clan_params)

        comb = (
            self._components.scheme,
            self._components.netloc,
            self._components.path,
            self._components.params,
            self._components.query,
            self._components.fragment,
        )
        match comb:
            case ("file", "", path, "", "", "") | ("", "", path, "", "", _):  # type: ignore
                self.scheme = ClanScheme.LOCAL.value(Path(path).expanduser().resolve())  # type: ignore
            case _:
                self.scheme = ClanScheme.REMOTE.value(self._components.geturl())  # type: ignore

    def get_internal(self) -> str:
        match self.scheme:
            case ClanScheme.LOCAL.value(path):
                return str(path)
            case ClanScheme.REMOTE.value(url):
                return url
            case _:
                raise ClanError(f"Unsupported uri components: {self.scheme}")

    def get_full_uri(self) -> str:
        return self._full_uri

    # TODO(@Qubasa): return a comparable id e.g. f"{url}#{attr}"
    # This should be our standard.
    def get_id(self) -> str:
        return f"{self._components.path}#{self._components.fragment}"

    @classmethod
    def from_path(
        cls,  # noqa
        path: Path,
        flake_attr: str | None = None,
        params: dict[str, Any] | ClanParameters | None = None,
    ) -> Self:
        return cls.from_str(str(path), flake_attr=flake_attr, params=params)

    @classmethod
    def from_str(
        cls,  # noqa
        url: str,
        flake_attr: str | None = None,
        params: dict[str, Any] | ClanParameters | None = None,
    ) -> Self:
        if flake_attr is not None and params is not None:
            raise ClanError("flake_attr and params are mutually exclusive")

        prefix = "clan://"
        if url.startswith(prefix):
            url = url[len(prefix) :]

        if params is None and flake_attr is None:
            return cls(f"clan://{url}")

        comp = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(comp.query)

        if isinstance(params, dict):
            query.update(params)
        elif isinstance(params, ClanParameters):
            query.update(params.__dict__)
        elif flake_attr is not None:
            query["flake_attr"] = [flake_attr]
        else:
            raise ClanError(f"Unsupported params type: {type(params)}")

        new_query = urllib.parse.urlencode(query, doseq=True)
        comp = comp._replace(query=new_query)
        new_url = urllib.parse.urlunparse(comp)
        return cls(f"clan://{new_url}")

    def __str__(self) -> str:
        return self.get_full_uri()

    def __repr__(self) -> str:
        return f"ClanURI({self.get_full_uri()})"
