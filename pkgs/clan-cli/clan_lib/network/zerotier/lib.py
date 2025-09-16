import contextlib
import json
import urllib.request
from typing import TypedDict


class ZeroTierConfig(TypedDict):
    clock: int
    online: bool
    version: str
    versionBuild: int
    versionMajor: int
    versionMinor: int
    versionRev: int


def get_zerotier_health() -> ZeroTierConfig:
    # Placeholder for actual ZeroTier running check
    res = urllib.request.urlopen("http://localhost:9993/health")
    return json.load(res)


def check_zerotier_running() -> bool:
    with contextlib.suppress(urllib.error.URLError):
        get_zerotier_health()
        return True
    return False
