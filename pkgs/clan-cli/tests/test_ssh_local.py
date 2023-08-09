import subprocess

from clan_cli.ssh import Group, Host, run


def test_run() -> None:
    p = run("echo hello")
    assert p.stdout is None


def test_run_failure() -> None:
    p = run("exit 1", check=False)
    assert p.returncode == 1

    try:
        p = run("exit 1")
    except Exception:
        pass
    else:
        assert False, "Command should have raised an error"


hosts = Group([Host("some_host")])


def test_run_environment() -> None:
    p1 = run("echo $env_var", stdout=subprocess.PIPE, extra_env=dict(env_var="true"))
    assert p1.stdout == "true\n"

    p2 = hosts.run_local(
        "echo $env_var", extra_env=dict(env_var="true"), stdout=subprocess.PIPE
    )
    assert p2[0].result.stdout == "true\n"

    p3 = hosts.run_local(
        ["env"], extra_env=dict(env_var="true"), stdout=subprocess.PIPE
    )
    assert "env_var=true" in p3[0].result.stdout


def test_run_non_shell() -> None:
    p = run(["echo", "$hello"], stdout=subprocess.PIPE)
    assert p.stdout == "$hello\n"


def test_run_stderr_stdout() -> None:
    p = run("echo 1; echo 2 >&2", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert p.stdout == "1\n"
    assert p.stderr == "2\n"


def test_run_local() -> None:
    hosts.run_local("echo hello")


def test_timeout() -> None:
    try:
        hosts.run_local("sleep 10", timeout=0.01)
    except Exception:
        pass
    else:
        assert False, "should have raised TimeoutExpired"


def test_run_function() -> None:
    def some_func(h: Host) -> bool:
        p = h.run_local("echo hello", stdout=subprocess.PIPE)
        return p.stdout == "hello\n"

    res = hosts.run_function(some_func)
    assert res[0].result


def test_run_exception() -> None:
    try:
        hosts.run_local("exit 1")
    except Exception:
        pass
    else:
        assert False, "should have raised Exception"


def test_run_function_exception() -> None:
    def some_func(h: Host) -> None:
        h.run_local("exit 1")

    try:
        hosts.run_function(some_func)
    except Exception:
        pass
    else:
        assert False, "should have raised Exception"


def test_run_local_non_shell() -> None:
    p2 = hosts.run_local(["echo", "1"], stdout=subprocess.PIPE)
    assert p2[0].result.stdout == "1\n"
