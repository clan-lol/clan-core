import pytest
from clan_cli.cmd import Log, RunOpts
from clan_cli.errors import ClanError, CmdOut
from clan_cli.ssh.host import Host
from clan_cli.ssh.host_group import HostGroup
from clan_cli.ssh.host_key import HostKeyCheck
from clan_cli.ssh.parse import parse_deployment_address


def test_parse_ipv6() -> None:
    host = parse_deployment_address("foo", "[fe80::1%eth0]:2222", HostKeyCheck.STRICT)
    assert host.host == "fe80::1%eth0"
    assert host.port == 2222
    host = parse_deployment_address("foo", "[fe80::1%eth0]", HostKeyCheck.STRICT)
    assert host.host == "fe80::1%eth0"
    assert host.port is None

    with pytest.raises(ClanError):
        # We instruct the user to use brackets for IPv6 addresses
        host = parse_deployment_address("foo", "fe80::1%eth0", HostKeyCheck.STRICT)


def test_run(host_group: HostGroup) -> None:
    proc = host_group.run_local(["echo", "hello"], RunOpts(log=Log.STDERR))
    assert proc[0].result.stdout == "hello\n"


def test_run_environment(host_group: HostGroup) -> None:
    p1 = host_group.run(
        ["echo $env_var"],
        RunOpts(shell=True, log=Log.STDERR),
        extra_env={"env_var": "true"},
    )
    assert p1[0].result.stdout == "true\n"
    p2 = host_group.run(["env"], RunOpts(log=Log.STDERR), extra_env={"env_var": "true"})
    assert "env_var=true" in p2[0].result.stdout


def test_run_no_shell(host_group: HostGroup) -> None:
    proc = host_group.run(["echo", "$hello"], RunOpts(log=Log.STDERR))
    assert proc[0].result.stdout == "$hello\n"


def test_run_function(host_group: HostGroup) -> None:
    def some_func(h: Host) -> bool:
        p = h.run(["echo", "hello"])
        return p.stdout == "hello\n"

    res = host_group.run_function(some_func)
    assert res[0].result


def test_timeout(host_group: HostGroup) -> None:
    try:
        host_group.run_local(["sleep", "10"], RunOpts(timeout=0.01))
    except Exception:
        pass
    else:
        msg = "should have raised TimeoutExpired"
        raise AssertionError(msg)


def test_run_exception(host_group: HostGroup) -> None:
    r = host_group.run(["exit 1"], RunOpts(check=False, shell=True))
    assert r[0].result.returncode == 1

    try:
        host_group.run(["exit 1"], RunOpts(shell=True))
    except Exception:
        pass
    else:
        msg = "should have raised Exception"
        raise AssertionError(msg)


def test_run_function_exception(host_group: HostGroup) -> None:
    def some_func(h: Host) -> CmdOut:
        return h.run_local(["exit 1"], RunOpts(shell=True))

    try:
        host_group.run_function(some_func)
    except Exception:
        pass
    else:
        msg = "should have raised Exception"
        raise AssertionError(msg)
