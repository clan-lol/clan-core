from urllib.parse import urlparse


def parse_moonlight_uri(uri: str) -> (str, str):
    print(uri)
    if uri.startswith("moonlight:"):
        # Fixes a bug where moonlight:// is not parsed correctly
        uri = uri[10:]
        uri = "moonlight://" + uri
    print(uri)
    parsed = urlparse(uri)
    if parsed.scheme != "moonlight":
        raise ValueError(f"Invalid moonlight URI: {uri}")
    hostname = parsed.hostname
    port = parsed.port
    return (hostname, port)
