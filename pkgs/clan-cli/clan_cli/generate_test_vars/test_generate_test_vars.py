import shutil
import subprocess
from pathlib import Path

import pytest
from clan_cli.generate_test_vars.cli import generate_test_vars


@pytest.mark.with_core
def test_generate_test_vars(
    clan_core: Path,
    temp_dir: Path,
) -> None:
    test_dir_original = clan_core / "checks/service-dummy-test"
    service_dir = temp_dir / "service-dummy-test"
    shutil.copytree(test_dir_original, service_dir)

    # Make the copied tree writable
    subprocess.run(["chmod", "-R", "+w", str(service_dir)], check=True)

    generate_test_vars(
        clean=True,
        repo_root=clan_core,
        test_dir=service_dir,
        check_attr="service-dummy-test",
    )
