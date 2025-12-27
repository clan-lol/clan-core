import json
import logging
import ssl
import urllib.request
from base64 import b64encode
from collections.abc import Iterator
from typing import Any, TypedDict, cast

from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.ssh.host import Host
from clan_lib.vars.get import VarNotFoundError, get_machine_var

log = logging.getLogger(__name__)


class MetricSample(TypedDict):
    fields: dict[str, Any]
    name: str
    tags: dict[str, str]
    timestamp: int


class MonitoringNotEnabledError(ClanError):
    pass


# Tests for this function are in the 'monitoring' clanService tests
def get_metrics(
    machine: Machine,
    target_host: Host,
) -> Iterator[MetricSample]:
    """Fetch Prometheus metrics from telegraf and return them as streaming metrics.

    Args:
        machine: The Machine instance to check.
        target_host: Remote instance representing the target host.

    Returns:
        Iterator[dict[str, Any]]: An iterator yielding parsed metric dictionaries line by line.

    """
    # Example: fetch Prometheus metrics with basic auth
    url = f"https://{target_host.address}:9990/telegraf.json"
    username = "prometheus"

    try:
        password_var = get_machine_var(machine, "telegraf/password")
        cert_var = get_machine_var(machine, "telegraf-certs/crt")
    except VarNotFoundError as e:
        msg = "Module 'monitoring' is required to fetch metrics from machine."
        raise MonitoringNotEnabledError(msg) from e

    if not password_var.exists or not cert_var.exists:
        msg = (
            f"Missing required var.\n"
            f"Ensure the 'monitoring' clanService is enabled and run `clan machines update {machine.name}`."
            "For more information, see: https://docs.clan.lol/reference/clanServices/monitoring/"
        )
        raise ClanError(msg)

    password = password_var.value.decode("utf-8")
    credentials = f"{username}:{password}"

    encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    cert_path = machine.select(
        "config.clan.core.vars.generators.telegraf-certs.files.crt.path"
    )
    context = ssl.create_default_context(cafile=cert_path)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED

    req = urllib.request.Request(url, headers=headers)  # noqa: S310

    try:
        machine.info(f"Fetching Prometheus metrics from {url}")
        with urllib.request.urlopen(req, context=context, timeout=10) as response:  # noqa: S310
            for line in response:
                line_str = line.decode("utf-8").strip()
                if line_str:
                    try:
                        yield cast("MetricSample", json.loads(line_str))
                    except json.JSONDecodeError:
                        machine.warn(f"Skipping invalid JSON line: {line_str}")
                        continue
    except Exception as e:
        msg = (
            f"Failed to fetch Prometheus metrics from {url}: {e}\n"
            "Ensure the telegraf.service is running and accessible."
        )
        raise ClanError(msg) from e
