import contextlib
import sys
from collections.abc import Generator
from typing import Any, NamedTuple

import pytest
from clan_cli.async_run import AsyncRuntime
from clan_cli.cmd import ClanCmdTimeoutError, Log, RunOpts
from clan_cli.errors import ClanError, CmdOut
from clan_cli.ssh.host import Host
from clan_cli.ssh.host_key import HostKeyCheck
from clan_cli.ssh.parse import parse_deployment_address


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
        def noop() -> Generator[None, Any, None]:
            yield

        maybe_check_exception = noop()  # type: ignore

    with maybe_check_exception:
        machine_name = "foo"
        result = parse_deployment_address(machine_name, test_addr, HostKeyCheck.STRICT)

    if expected_exception:
        return

    assert result.host == expected_host
    assert result.port == expected_port
    assert result.user == expected_user or (
        expected_user == "" and result.user == "root"
    )
    assert result.ssh_options == expected_options


def test_parse_ssh_options() -> None:
    addr = "root@example.com:2222?IdentityFile=/path/to/private/key&StrictHostKeyChecking=yes"
    host = parse_deployment_address("foo", addr, HostKeyCheck.STRICT)
    assert host.host == "example.com"
    assert host.port == 2222
    assert host.user == "root"
    assert host.ssh_options["IdentityFile"] == "/path/to/private/key"
    assert host.ssh_options["StrictHostKeyChecking"] == "yes"


is_darwin = sys.platform == "darwin"


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_run(hosts: list[Host], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None, host.run_local, ["echo", "hello"], RunOpts(log=Log.STDERR)
        )
    assert proc.wait().result.stdout == "hello\n"


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_run_environment(hosts: list[Host], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None,
            host.run_local,
            ["echo $env_var"],
            RunOpts(shell=True, log=Log.STDERR),
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


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_run_no_shell(hosts: list[Host], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None, host.run_local, ["echo", "hello"], RunOpts(log=Log.STDERR)
        )
    assert proc.wait().result.stdout == "hello\n"


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_run_function(hosts: list[Host], runtime: AsyncRuntime) -> None:
    def some_func(h: Host) -> bool:
        p = h.run(["echo", "hello"])
        return p.stdout == "hello\n"

    for host in hosts:
        proc = runtime.async_run(None, some_func, host)
    assert proc.wait().result


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_timeout(hosts: list[Host], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None, host.run_local, ["sleep", "10"], RunOpts(timeout=0.01)
        )
    error = proc.wait().error
    assert isinstance(error, ClanCmdTimeoutError)


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_run_exception(hosts: list[Host], runtime: AsyncRuntime) -> None:
    for host in hosts:
        proc = runtime.async_run(
            None, host.run_local, ["exit 1"], RunOpts(shell=True, check=False)
        )
    assert proc.wait().result.returncode == 1

    try:
        for host in hosts:
            runtime.async_run(None, host.run_local, ["exit 1"], RunOpts(shell=True))
        runtime.join_all()
        runtime.check_all()
    except Exception:
        pass
    else:
        msg = "should have raised Exception"
        raise AssertionError(msg)


@pytest.mark.skipif(is_darwin, reason="preload doesn't work on darwin")
def test_run_function_exception(hosts: list[Host], runtime: AsyncRuntime) -> None:
    def some_func(h: Host) -> CmdOut:
        return h.run_local(["exit 1"], RunOpts(shell=True))

    try:
        for host in hosts:
            runtime.async_run(None, some_func, host)
        runtime.join_all()
        runtime.check_all()
    except Exception:
        pass
    else:
        msg = "should have raised Exception"
        raise AssertionError(msg)
