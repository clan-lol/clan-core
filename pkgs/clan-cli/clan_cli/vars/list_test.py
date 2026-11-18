from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from clan_cli.tests.helpers import cli
from clan_cli.vars import list as list_mod
from clan_lib.errors import ClanError
from clan_lib.vars._types import GeneratorId, PerExport, PerMachine, Placement, Shared
from clan_lib.vars.generator import Generator
from clan_lib.vars.var import Var

if TYPE_CHECKING:
    from clan_lib.vars._types import StoreBase


def test_list_command_no_flake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["vars", "list", "machine1"])


class FakeStore:
    """Store stub that only answers the 2 questions the renderer asks."""

    def __init__(self, values: dict[tuple[GeneratorId, str], bytes]) -> None:
        self.values = values

    def exists(self, generator: GeneratorId, name: str) -> bool:
        return (generator, name) in self.values

    def get(self, generator: GeneratorId, name: str) -> bytes:
        return self.values[(generator, name)]


def make_generator(
    name: str,
    placement: Placement,
    files: list[Var],
    store: FakeStore,
) -> Generator:
    generator = Generator(key=GeneratorId(name=name, placement=placement), files=files)
    for var in files:
        var.store(cast("StoreBase", store))
        var.generator(generator)
    return generator


@pytest.fixture
def no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(list_mod, "DISABLE_COLOR", True)


@pytest.mark.usefixtures("no_color")
def test_render_groups_every_placement() -> None:
    shared_id = GeneratorId(name="root-ca", placement=Shared())
    machine_id = GeneratorId(name="wifi", placement=PerMachine(machine="jon"))
    export_id = GeneratorId(name="network-id", placement=PerExport(exports_key="zt:a"))
    store = FakeStore(
        {
            (shared_id, "cert"): b"CA-CERT",
            (machine_id, "password"): b"secret",
            (export_id, "id"): b"0123",
        },
    )
    generators = [
        make_generator(
            "root-ca",
            Shared(),
            [
                Var(
                    id="root-ca/cert",
                    name="cert",
                    machines=["jon"],
                    secret=False,
                    deploy=True,
                ),
            ],
            store,
        ),
        make_generator(
            "wifi",
            PerMachine(machine="jon"),
            [
                Var(
                    id="wifi/password",
                    name="password",
                    machines=["jon"],
                    secret=True,
                    deploy=True,
                ),
            ],
            store,
        ),
        make_generator(
            "network-id",
            PerExport(exports_key="zt:a"),
            [
                Var(
                    id="network-id/id",
                    name="id",
                    machines=[],
                    secret=False,
                    deploy=True,
                ),
            ],
            store,
        ),
    ]

    lines = list_mod.render_clan_vars(generators)
    out = "\n".join(lines)

    assert "Shared" in out
    assert "Per-Machine" in out
    assert "Per-Export" in out
    assert "jon" in out
    assert "zt:a" in out
    # The legend explains the parentheses
    assert "(machines) = where the var will be deployed" in out
    # A per-machine var leaves the machine out, the tree already shows it
    assert "● password" in out
    assert "(jon)" not in out.split("Per-Machine")[1]
    # A shared var names every machine it is deployed to
    assert any("○ cert" in line and line.endswith("(jon)") for line in lines)
    # No value is ever printed
    assert "CA-CERT" not in out
    assert "0123" not in out


@pytest.mark.usefixtures("no_color")
def test_render_marks_vars_that_are_not_generated() -> None:
    store = FakeStore({})
    generators = [
        make_generator(
            "wifi",
            PerMachine(machine="jon"),
            [
                Var(
                    id="wifi/ssid",
                    name="ssid",
                    machines=["jon"],
                    secret=False,
                    deploy=True,
                ),
                Var(
                    id="wifi/password",
                    name="password",
                    machines=["jon"],
                    secret=True,
                    deploy=True,
                ),
            ],
            store,
        ),
    ]

    lines = list_mod.render_clan_vars(generators)
    assert any("○ ssid" in line and line.endswith("not generated") for line in lines)
    assert any(
        "● password" in line and line.endswith("not generated") for line in lines
    )


@pytest.mark.usefixtures("no_color")
def test_render_marks_vars_without_deploy_target() -> None:
    gen_id = GeneratorId(name="ca", placement=Shared())
    store = FakeStore({(gen_id, "key"): b"KEY"})
    generators = [
        make_generator(
            "ca",
            Shared(),
            [
                Var(
                    id="ca/key",
                    name="key",
                    machines=["jon"],
                    secret=True,
                    deploy=False,
                ),
            ],
            store,
        ),
    ]

    lines = list_mod.render_clan_vars(generators)
    out = "\n".join(lines)

    assert any("● key" in line and line.endswith("no-deploy") for line in lines)
    # A var that is not deployed names no machine
    assert "jon" not in out


@pytest.mark.usefixtures("no_color")
def test_render_never_prints_a_value() -> None:
    gen_id = GeneratorId(name="gen", placement=Shared())
    store = FakeStore(
        {
            (gen_id, "text"): b"line1\nline2\nline3",
            (gen_id, "blob"): b"\x80\x81",
        },
    )
    generators = [
        make_generator(
            "gen",
            Shared(),
            [
                Var(
                    id="gen/text",
                    name="text",
                    machines=[],
                    secret=False,
                    deploy=True,
                ),
                Var(
                    id="gen/blob",
                    name="blob",
                    machines=[],
                    secret=False,
                    deploy=True,
                ),
            ],
            store,
        ),
    ]

    out = "\n".join(list_mod.render_clan_vars(generators))

    assert "line1" not in out
    assert out.endswith("○ text")
    assert "○ blob\n" in out


@pytest.mark.usefixtures("no_color")
def test_render_aligns_the_columns_across_every_scope() -> None:
    """`no-deploy` starts at the same column in every row of the whole tree."""
    store = FakeStore({})
    generators = [
        make_generator(
            "root-ca",
            Shared(),
            [Var(id="root-ca/key", name="key", machines=["jon"], secret=True)],
            store,
        ),
        make_generator(
            "a-very-long-generator-name",
            PerMachine(machine="jon"),
            [
                Var(
                    id="a-very-long-generator-name/a-very-long-file-name",
                    name="a-very-long-file-name",
                    machines=["jon"],
                    secret=True,
                ),
            ],
            store,
        ),
        make_generator(
            "network-id",
            PerExport(exports_key="zt:a"),
            [Var(id="network-id/id", name="id", machines=[], secret=False)],
            store,
        ),
    ]

    lines = list_mod.render_clan_vars(generators)

    deploy_columns = {line.index("no-deploy") for line in lines if "no-deploy" in line}
    assert len(deploy_columns) == 1
    state_columns = {
        line.index("not generated") for line in lines if "not generated" in line
    }
    assert len(state_columns) == 1
    # 3 scopes, 3 generators, 3 vars
    assert len([line for line in lines if "no-deploy" in line]) == 3


@pytest.mark.usefixtures("no_color")
def test_render_without_any_generator() -> None:
    assert list_mod.render_clan_vars([]) == ["No vars found"]
