from urllib.error import HTTPError
from urllib.request import urlopen

from .network import NetworkTechnologyBase


class NetworkTechnology(NetworkTechnologyBase):
    socks_port: int
    command_port: int

    def is_running(self) -> bool:
        """Check if Tor is running by sending HTTP request to SOCKS port."""
        try:
            response = urlopen("http://127.0.0.1:9050", timeout=5)
            content = response.read().decode("utf-8", errors="ignore")
            return "tor" in content.lower()
        except HTTPError as e:
            return "tor" in str(e).lower()
        except Exception:
            return False
