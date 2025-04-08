import json
import os
from pathlib import Path

import pytest
from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.tests.helpers import cli


class KeyPair:
    def __init__(self, pubkey: str, privkey: str) -> None:
        self.pubkey = pubkey
        self.privkey = privkey


class SopsSetup:
    """Hold a list of three key pairs and create an "admin" user in the clan.

    The first key in the list is used as the admin key and
    the private part of the key is exposed in the
    `SOPS_AGE_KEY` environment variable, the two others can
    be used to add machines or other users.
    """

    def __init__(self, keys: list[KeyPair]) -> None:
        self.keys = keys
        self.user = os.environ.get("USER", "admin")

    def init(self, flake_path: Path) -> None:
        cli.run(
            [
                "vars",
                "keygen",
                "--flake",
                str(flake_path),
                "--user",
                self.user,
            ]
        )


KEYS = [
    KeyPair(
        "age1dhwqzkah943xzc34tc3dlmfayyevcmdmxzjezdgdy33euxwf59vsp3vk3c",
        "AGE-SECRET-KEY-1KF8E3SR3TTGL6M476SKF7EEMR4H9NF7ZWYSLJUAK8JX276JC7KUSSURKFK",
    ),
    KeyPair(
        "age14tva0txcrl0zes05x7gkx56qd6wd9q3nwecjac74xxzz4l47r44sv3fz62",
        "AGE-SECRET-KEY-1U5ENXZQAY62NC78Y2WC0SEGRRMAEEKH79EYY5TH4GPFWJKEAY0USZ6X7YQ",
    ),
    KeyPair(
        "age1dhuh9xtefhgpr2sjjf7gmp9q2pr37z92rv4wsadxuqdx48989g7qj552qp",
        "AGE-SECRET-KEY-169N3FT32VNYQ9WYJMLUSVTMA0TTZGVJF7YZWS8AHTWJ5RR9VGR7QCD8SKF",
    ),
]


@pytest.fixture
def age_keys() -> list[KeyPair]:
    return KEYS


@pytest.fixture
def sops_setup(
    monkeypatch: pytest.MonkeyPatch,
) -> SopsSetup:
    monkeypatch.setenv("SOPS_AGE_KEY", KEYS[0].privkey)
    return SopsSetup(KEYS)


# louis@(2025-03-10): right now this is specific to the `sops/secrets` folder,
# but we could make it generic to any sops file if the need arises.
def assert_secrets_file_recipients(
    flake_path: Path,
    secret_name: str,
    expected_age_recipients_keypairs: list["KeyPair"],
    err_msg: str | None = None,
) -> None:
    """Checks that the recipients of a secrets file matches expectations.

    This looks up the `secret` file for `secret_name` in the `sops` directory
    under `flake_path`.

    :param err_msg: in case of failure, if you gave an error message then it
       will be displayed, otherwise pytest will display the two different sets
       of recipients.
    """
    sops_file = sops_secrets_folder(flake_path) / secret_name / "secret"
    with sops_file.open("rb") as fp:
        sops_data = json.load(fp)
    age_recipients = {each["recipient"] for each in sops_data["sops"]["age"]}
    expected_age_recipients = {pair.pubkey for pair in expected_age_recipients_keypairs}
    if not err_msg:
        assert age_recipients == expected_age_recipients
        return
    assert age_recipients == expected_age_recipients, err_msg
