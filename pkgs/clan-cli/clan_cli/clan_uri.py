# Import the urllib.parse, enum and dataclasses modules
import dataclasses
import urllib.parse
from dataclasses import dataclass
from enum import Enum, member
from pathlib import Path
from typing import Self

from .errors import ClanError


# Define an enum with different members that have different values
class ClanScheme(Enum):
    # Use the dataclass decorator to add fields and methods to the members
    @member
    @dataclass
    class HTTP:
        url: str  # The url field holds the HTTP URL

        def __str__(self) -> str:
            return f"HTTP({self.url})"  # The __str__ method returns a custom string representation

    @member
    @dataclass
    class FILE:
        path: Path  # The path field holds the local path

        def __str__(self) -> str:
            return f"FILE({self.path})"  # The __str__ method returns a custom string representation


# Parameters defined here will be DELETED from the nested uri
# so make sure there are no conflicts with other webservices
@dataclass
class ClanParameters:
    flake_attr: str = "defaultVM"


# Define the ClanURI class
class ClanURI:
    # Initialize the class with a clan:// URI
    def __init__(self, uri: str) -> None:
        # Check if the URI starts with clan://
        if uri.startswith("clan://"):
            self._nested_uri = uri[7:]
        else:
            raise ClanError(f"Invalid scheme: expected clan://, got {uri}")

        # Parse the URI into components
        # scheme://netloc/path;parameters?query#fragment
        self._components = urllib.parse.urlparse(self._nested_uri)

        # Parse the query string into a dictionary
        query = urllib.parse.parse_qs(self._components.query)

        params: dict[str, str] = {}
        for field in dataclasses.fields(ClanParameters):
            if field.name in query:
                values = query[field.name]
                if len(values) > 1:
                    raise ClanError(f"Multiple values for parameter: {field.name}")
                params[field.name] = values[0]

                # Remove the field from the query dictionary
                # clan uri and nested uri share one namespace for query parameters
                # we need to make sure there are no conflicts
                del query[field.name]

        new_query = urllib.parse.urlencode(query, doseq=True)
        self._components = self._components._replace(query=new_query)
        self.params = ClanParameters(**params)

        comb = (
            self._components.scheme,
            self._components.netloc,
            self._components.path,
            self._components.params,
            self._components.query,
            self._components.fragment,
        )

        match comb:
            case ("http" | "https", _, _, _, _, _):
                self.scheme = ClanScheme.HTTP.value(self._components.geturl())  # type: ignore
            case ("file", "", path, "", "", "") | ("", "", path, "", "", ""):  # type: ignore
                self.scheme = ClanScheme.FILE.value(Path(path))  # type: ignore
            case _:
                raise ClanError(f"Unsupported uri components: {comb}")

    def get_internal(self) -> str:
        return self._nested_uri

    @classmethod
    def from_path(cls, path: Path, params: ClanParameters) -> Self:  # noqa
        urlparams = urllib.parse.urlencode(params.__dict__)
        return cls(f"clan://{path}?{urlparams}")

    def __str__(self) -> str:
        return f"ClanURI({self._components.geturl()})"
