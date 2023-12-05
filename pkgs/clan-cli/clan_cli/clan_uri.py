# Import the urllib.parse, enum and dataclasses modules
import dataclasses
import urllib.parse
from dataclasses import dataclass
from enum import Enum, member
from pathlib import Path
from typing import Dict

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
    class HTTPS:
        url: str  # The url field holds the HTTPS URL

        def __str__(self) -> str:
            return f"HTTPS({self.url})"  # The __str__ method returns a custom string representation

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
    flake_attr: str | None
    machine: str | None


# Define the ClanURI class
class ClanURI:
    # Initialize the class with a clan:// URI
    def __init__(self, uri: str) -> None:
        # Check if the URI starts with clan://
        if uri.startswith("clan://"):
            self._nested_uri = uri[7:]
        else:
            raise ClanError("Invalid scheme: expected clan://, got {}".format(uri))

        # Parse the URI into components
        # scheme://netloc/path;parameters?query#fragment
        self._components = urllib.parse.urlparse(self._nested_uri)

        # Parse the query string into a dictionary
        self._query = urllib.parse.parse_qs(self._components.query)

        params: Dict[str, str | None] = {}
        for field in dataclasses.fields(ClanParameters):
            if field.name in self._query:
                # Check if the field type is a list
                if issubclass(field.type, list):
                    setattr(params, field.name, self._query[field.name])
                # Check if the field type is a single value
                else:
                    values = self._query[field.name]
                    if len(values) > 1:
                        raise ClanError(
                            "Multiple values for parameter: {}".format(field.name)
                        )
                    setattr(params, field.name, values[0])

                # Remove the field from the query dictionary
                # clan uri and nested uri share one namespace for query parameters
                # we need to make sure there are no conflicts
                del self._query[field.name]
            else:
                params[field.name] = None

        self.params = ClanParameters(**params)

        # Use the match statement to check the scheme and create a ClanScheme member with the value
        match self._components.scheme:
            case "http":
                self.scheme = ClanScheme.HTTP.value(self._components.geturl())  # type: ignore
            case "https":
                self.scheme = ClanScheme.HTTPS.value(self._components.geturl())  # type: ignore
            case "file":
                self.scheme = ClanScheme.FILE.value(Path(self._components.path))  # type: ignore
            case _:
                raise ClanError(
                    "Unsupported scheme: {}".format(self._components.scheme)
                )
