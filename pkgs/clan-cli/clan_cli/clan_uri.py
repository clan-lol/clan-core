# Import the urllib.parse, enum and dataclasses modules
import dataclasses
import urllib.parse
from dataclasses import dataclass
from enum import Enum, member
from pathlib import Path
from typing import Self
import urllib.request


from .errors import ClanError


def url_ok(url: str):
    # Create a request object with the URL and the HEAD method
    req = urllib.request.Request(url, method="HEAD")
    try:
        # Open the URL and get the response object
        res = urllib.request.urlopen(req)
        # Return True if the status code is 200 (OK)
        if not res.status_code == 200:
            raise ClanError(f"URL has status code: {res.status_code}")
    except urllib.error.URLError as ex:
        raise ClanError(f"URL error: {ex}")


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
        self._full_uri = uri
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

        new_params: dict[str, str] = {}
        for field in dataclasses.fields(ClanParameters):
            if field.name in query:
                values = query[field.name]
                if len(values) > 1:
                    raise ClanError(f"Multiple values for parameter: {field.name}")
                new_params[field.name] = values[0]

                # Remove the field from the query dictionary
                # clan uri and nested uri share one namespace for query parameters
                # we need to make sure there are no conflicts
                del query[field.name]

        new_query = urllib.parse.urlencode(query, doseq=True)
        self._components = self._components._replace(query=new_query)
        self.params = ClanParameters(**new_params)

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

    def check_exits(self):
        match self.scheme:
            case ClanScheme.FILE.value(path):
                if not path.exists():
                    raise ClanError(f"File does not exist: {path}")
            case ClanScheme.HTTP.value(url):
                return url_ok(url)

    def get_internal(self) -> str:
        match self.scheme:
            case ClanScheme.FILE.value(path):
                return str(path)  # type: ignore
            case ClanScheme.HTTP.value(url):
                return url  # type: ignore
            case _:
                raise ClanError(f"Unsupported uri components: {self.scheme}")

    def get_full_uri(self) -> str:
        return self._full_uri

    @classmethod
    def from_path(cls, path: Path, params: ClanParameters | None = None) -> Self:  # noqa
        return cls.from_str(str(path), params)

    @classmethod
    def from_str(cls, url: str, params: ClanParameters | None = None) -> Self:  # noqa
        prefix = "clan://"
        if url.startswith(prefix):
            url = url[len(prefix) :]

        if params is None:
            return cls(f"clan://{url}")

        comp = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(comp.query)
        query.update(params.__dict__)
        new_query = urllib.parse.urlencode(query, doseq=True)
        comp = comp._replace(query=new_query)
        new_url = urllib.parse.urlunparse(comp)
        return cls(f"clan://{new_url}")

    def __str__(self) -> str:
        return self.get_full_uri()
