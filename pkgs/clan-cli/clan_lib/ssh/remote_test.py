import contextlib
import sys
from collections.abc import Generator
from typing import Any, NamedTuple

import pytest

from clan_lib.async_run import AsyncRuntime
from clan_lib.cmd import ClanCmdTimeoutError, Log, RunOpts
from clan_lib.errors import ClanError, CmdOut
from clan_lib.ssh.remote import Remote
from clan_lib.ssh.sudo_askpass_proxy import SudoAskpassProxy

if sys.platform == "darwin":
    pytest.skip("preload doesn't work on darwin", allow_module_level=True)


class ParseTestCase(NamedTuple):
    test_addr: str = ""
    expected_host: str = ""
    expected_port: int | None = None
    expected_user: str = ""
    expected_options: dict[str, str] = {}  # noqa: RUF012
    expected_exception: type[Exception] | None = None


parse_deployment_address_test_cases = (
    (
        "host_only",
        ParseTestCase(test_addr="example.com", expected_host="example.com"),
    ),
    (
        "host_user_port",
        ParseTestCase(
            test_addr="user@example.com:22",
            expected_host="example.com",
            expected_user="user",
            expected_port=22,
        ),
    ),
    (
        "cannot_parse_user_host_port",
        ParseTestCase(test_addr="foo@bar@wat", expected_exception=ClanError),
    ),
    (
        "missing_hostname",
        ParseTestCase(test_addr="foo@:2222", expected_exception=ClanError),
    ),
    (
        "invalid_ipv6",
        ParseTestCase(test_addr="user@fe80::1%eth0", expected_exception=ClanError),
    ),
    (
        "valid_ipv6_without_port",
        ParseTestCase(test_addr="[fe80::1%eth0]", expected_host="fe80::1%eth0"),
    ),
    (
        "valid_ipv6_with_port",
        ParseTestCase(
            test_addr="[fe80::1%eth0]:222",
            expected_host="fe80::1%eth0",
            expected_port=222,
        ),
    ),
    (
        "empty_options",
        ParseTestCase(test_addr="example.com?", expected_host="example.com"),
    ),
    (
        "option_with_missing_value",
        ParseTestCase(test_addr="example.com?foo", expected_exception=ClanError),
    ),
    (
        "options_with_@",
        ParseTestCase(
            test_addr="user@example.com?ProxyJump=root@foo&IdentityFile=/key",
            expected_host="example.com",
            expected_user="user",
            expected_options={
                "IdentityFile": "/key",
                "ProxyJump": "root@foo",
            },
        ),
    ),
)


@pytest.mark.parametrize(
    argnames=ParseTestCase._fields,
    argvalues=(case for _, case in parse_deployment_address_test_cases),
    ids=(name for name, _ in parse_deployment_address_test_cases),
)
def test_parse_deployment_address(
    test_addr: str,
    expected_host: str,
    expected_port: int | None,
    expected_user: str,
    expected_options: dict[str, str],
    expected_exception: type[Exception] | None,
) -> None:
    if expected_exception:
        maybe_check_exception = pytest.raises(expected_exception)
    else:

        @contextlib.contextmanager
        def noop() -> Generator[None, Any]:
            yield

        maybe_check_exception = noop()  # type: ignore[assignment]

    with maybe_check_exception:
        machine_name = "foo"
        result = Remote.from_ssh_uri(
            machine_name=machine_name,
            address=test_addr,
        ).override(host_key_check="strict")

    if expected_exception:
        return

    assert result.address == expected_host
    assert result.port == expected_port
    assert result.user == expected_user or (
        expected_user == "" and result.user == "root"
    )

    for key, value in expected_options.items():
        assert result.ssh_options[key] == value


def test_parse_ssh_options() -> None:
    addr = "root@example.com:2222?IdentityFile=/path/to/private/key&StrictRemoteKeyChecking=yes"
    host = Remote.from_ssh_uri(machine_name="foo", address=addr).override(
        host_key_check="strict",
    )
    assert host.address == "example.com"
    assert host.port == 2222
    assert host.user == "root"
    assert host.ssh_options["IdentityFile"] == "/path/to/private/key"
    assert host.ssh_options["StrictRemoteKeyChecking"] == "yes"


def test_run(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None,
            host.run_local,
            ["echo", "hello"],
            RunOpts(log=Log.STDERR),
        )
    assert proc.wait().result.stdout == "hello\n"


def test_run_environment(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None,
            host.run_local,
            ["echo $env_var"],
            RunOpts(shell=True, log=Log.STDERR),  # noqa: S604
            extra_env={"env_var": "true"},
        )
    assert proc.wait().result.stdout == "true\n"

    for host in hosts:
        p2 = runtime.async_run(
            None,
            host.run_local,
            ["env"],
            RunOpts(log=Log.STDERR),
            extra_env={"env_var": "true"},
        )
    assert "env_var=true" in p2.wait().result.stdout


def test_run_no_shell(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None,
            host.run_local,
            ["echo", "hello"],
            RunOpts(log=Log.STDERR),
        )
    assert proc.wait().result.stdout == "hello\n"


def test_sudo_ask_proxy(hosts: list[Remote]) -> None:
    host = hosts[0]
    with host.host_connection() as host:
        proxy = SudoAskpassProxy(host, prompt_command=["bash", "-c", "echo yes"])

        try:
            askpass_path = proxy.run()
            out = host.run(
                ["bash", "-c", askpass_path],
                opts=RunOpts(check=False, log=Log.BOTH),
            )
            assert out.returncode == 0
            assert out.stdout == "yes\n"
        finally:
            proxy.cleanup()


def test_run_function(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    def some_func(h: Remote) -> bool:
        with h.host_connection() as ssh:
            p = ssh.run(["echo", "hello"])
        return p.stdout == "hello\n"

    for host in hosts:
        proc = runtime.async_run(None, some_func, host)
    assert proc.wait().result


def test_timeout(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None,
            host.run_local,
            ["sleep", "10"],
            RunOpts(timeout=0.01),
        )
    error = proc.wait().error
    assert isinstance(error, ClanCmdTimeoutError)


def test_run_exception(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None,
            host.run_local,
            ["exit 1"],
            RunOpts(shell=True, check=False),  # noqa: S604
        )
    assert proc.wait().result.returncode == 1

    try:
        for host in hosts:
            runtime.async_run(None, host.run_local, ["exit 1"], RunOpts(shell=True))  # noqa: S604
        runtime.join_all()
        runtime.check_all()
    except ClanError:
        pass
    else:
        msg = "should have raised Exception"
        raise AssertionError(msg)


def test_run_function_exception(hosts: list[Remote], runtime: AsyncRuntime) -> None:
    def some_func(h: Remote) -> CmdOut:
        return h.run_local(["exit 1"], RunOpts(shell=True))  # noqa: S604

    try:
        for host in hosts:
            runtime.async_run(None, some_func, host)
        runtime.join_all()
        runtime.check_all()
    except ClanError:
        pass
    else:
        msg = "should have raised Exception"
        raise AssertionError(msg)
