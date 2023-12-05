# Import the urllib.parse module
import urllib.parse
from enum import Enum

from .errors import ClanError


class ClanScheme(Enum):
    HTTP = "http"
    HTTPS = "https"
    FILE = "file"


# Define the ClanURI class
class ClanURI:
    # Initialize the class with a clan:// URI
    def __init__(self, uri: str) -> None:
        if uri.startswith("clan://"):
            uri = uri[7:]
        else:
            raise ClanError("Invalid scheme: expected clan://, got {}".format(uri))

        # Parse the URI into components
        self.components = urllib.parse.urlparse(uri)

        try:
            self.scheme = ClanScheme(self.components.scheme)
        except ValueError:
            raise ClanError("Unsupported scheme: {}".format(self.components.scheme))

    # Define a method to get the path of the URI
    @property
    def path(self) -> str:
        return self.components.path

    @property
    def url(self) -> str:
        return self.components.geturl()

    # Define a method to check if the URI is a remote HTTP URL
    def is_remote(self) -> bool:
        match self.scheme:
            case ClanScheme.HTTP | ClanScheme.HTTPS:
                return True
            case ClanScheme.FILE:
                return False

    # Define a method to check if the URI is a local path
    def is_local(self) -> bool:
        return not self.is_remote()
