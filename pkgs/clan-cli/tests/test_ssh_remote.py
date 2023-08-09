import os
import pwd
import subprocess

from sshd import Sshd

from clan_cli.ssh import Group, Host, HostKeyCheck


def deploy_group(sshd: Sshd) -> Group:
    login = pwd.getpwuid(os.getuid()).pw_name
    return Group(
        [
            Host(
                "127.0.0.1",
                port=sshd.port,
                user=login,
                key=sshd.key,
                host_key_check=HostKeyCheck.NONE,
            )
        ]
    )


def test_run(sshd: Sshd) -> None:
    g = deploy_group(sshd)
    proc = g.run("echo hello", stdout=subprocess.PIPE)
    assert proc[0].result.stdout == "hello\n"


def test_run_environment(sshd: Sshd) -> None:
    g = deploy_group(sshd)
    p1 = g.run("echo $env_var", stdout=subprocess.PIPE, extra_env=dict(env_var="true"))
    assert p1[0].result.stdout == "true\n"
    p2 = g.run(["env"], stdout=subprocess.PIPE, extra_env=dict(env_var="true"))
    assert "env_var=true" in p2[0].result.stdout


def test_run_no_shell(sshd: Sshd) -> None:
    g = deploy_group(sshd)
    proc = g.run(["echo", "$hello"], stdout=subprocess.PIPE)
    assert proc[0].result.stdout == "$hello\n"


def test_run_function(sshd: Sshd) -> None:
    def some_func(h: Host) -> bool:
        p = h.run("echo hello", stdout=subprocess.PIPE)
        return p.stdout == "hello\n"

    g = deploy_group(sshd)
    res = g.run_function(some_func)
    assert res[0].result


def test_timeout(sshd: Sshd) -> None:
    g = deploy_group(sshd)
    try:
        g.run_local("sleep 10", timeout=0.01)
    except Exception:
        pass
    else:
        assert False, "should have raised TimeoutExpired"


def test_run_exception(sshd: Sshd) -> None:
    g = deploy_group(sshd)

    r = g.run("exit 1", check=False)
    assert r[0].result.returncode == 1

    try:
        g.run("exit 1")
    except Exception:
        pass
    else:
        assert False, "should have raised Exception"


def test_run_function_exception(sshd: Sshd) -> None:
    def some_func(h: Host) -> subprocess.CompletedProcess[str]:
        return h.run_local("exit 1")

    g = deploy_group(sshd)

    try:
        g.run_function(some_func)
    except Exception:
        pass
    else:
        assert False, "should have raised Exception"
