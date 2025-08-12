from clan_lib.cmd import RunOpts
from clan_lib.ssh.localhost import LocalHost


def test_localhost() -> None:
    # Create LocalHost instance
    localhost = LocalHost(command_prefix="local-test")
    # Test basic command execution
    result = localhost.run(["echo", "Hello from LocalHost"])
    assert result.returncode == 0, f"Command failed with code {result.returncode}"
    assert result.stdout.strip() == "Hello from LocalHost", (
        f"Unexpected output: {result.stdout}"
    )
    # Test with environment variable
    result = localhost.run(
        ["printenv", "TEST_VAR"],
        opts=RunOpts(check=False),  # Don't check return code
        extra_env={"TEST_VAR": "LocalHost works!"},
    )
    assert result.returncode == 0, f"Command failed with code {result.returncode}"
    assert result.stdout.strip() == "LocalHost works!", (
        f"Expected 'LocalHost works!', got '{result.stdout.strip()}'"
    )
