import re
import textwrap

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake
from clan_cli.tests.helpers import cli
from clan_lib.flake import Flake
from clan_lib.vars.generate import run_flake_generators

ANSI = re.compile(r"\033\[[0-9;]*m")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_vars_list_covers_every_placement(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    capsys: pytest.CaptureFixture,
) -> None:
    """`clan vars list` without a machine lists shared, per-machine and per-export vars."""
    flake = flake_with_sops
    flake.clan_nix_raw = textwrap.dedent(r"""
        { self, ... }:
        let
            clan-core = self.inputs.clan-core;
        in
        {
            machines.jon = {
                clan.core.vars.generators.wifi = {
                    files.ssid.secret = false;
                    files.password.deploy = true;
                    script = ''
                        echo "home-network" > $out/ssid
                        echo "s3cret" > $out/password
                    '';
                };
                clan.core.vars.generators.root-ca = {
                    share = true;
                    files.cert.secret = false;
                    files.key.deploy = false;
                    script = ''
                        echo "CA-CERT-BODY" > $out/cert
                        echo "CA-KEY-BODY" > $out/key
                    '';
                };
            };
            machines.sara = { };
            exports."zerotier:default:controller:jon" = {
              imports = [ (clan-core + "/modules/clan/export-modules/generators.nix") ];
              generators.network-id = {
                files.id.secret = false;
                files.token = { deploy = [ "jon" ]; };
                script = ''
                  echo "0123456789abcdef" > $out/id
                  echo "api-token" > $out/token
                '';
              };
            };
        }
    """)
    flake.refresh()
    monkeypatch.chdir(flake.path)

    flake_obj = Flake(str(flake.path))
    cli.run(["vars", "generate", "--flake", str(flake.path)])
    run_flake_generators(flake_obj, True)

    capsys.readouterr()
    cli.run(["vars", "list", "--flake", str(flake.path)])
    out = ANSI.sub("", capsys.readouterr().out)

    assert "Shared" in out
    assert "Per-Machine" in out
    assert "Per-Export" in out
    # A shared public var is deployed to every machine that declares it
    assert "○ cert  (jon)" in out
    assert "● key   no-deploy" in out
    # per-machine scope, grouped by machine and generator, without the machine
    assert "jon" in out
    assert "○ ssid" in out
    assert "● password" in out
    assert "(jon)" not in out.split("Per-Machine")[1].split("Per-Export")[0]
    # per-export scope, keyed by the export key
    assert "zerotier:default:controller:jon" in out
    assert "○ id     no-deploy" in out
    assert "● token  (jon)" in out
    # no value is ever printed, public or secret
    assert "home-network" not in out
    assert "0123456789abcdef" not in out
    assert "s3cret" not in out
    assert "api-token" not in out
    assert "CA-KEY-BODY" not in out

    # With a machine the flat listing is unchanged
    capsys.readouterr()
    cli.run(["vars", "list", "jon", "--flake", str(flake.path)])
    machine_out = ANSI.sub("", capsys.readouterr().out)
    assert "wifi/ssid: home-network" in machine_out
    assert "wifi/password: ********" in machine_out
