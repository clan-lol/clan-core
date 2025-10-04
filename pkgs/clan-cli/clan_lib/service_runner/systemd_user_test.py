import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clan_lib.errors import ClanError

from .systemd_user import SystemdUserService


@pytest.fixture
def service_runner(temporary_home: Path) -> SystemdUserService:
    """Create a ServiceRunner instance with temporary home directory"""
    systemd_dir = temporary_home / ".config" / "systemd" / "user"
    return SystemdUserService(user_systemd_dir=systemd_dir)


@pytest.fixture
def systemd_service(temporary_home: Path) -> SystemdUserService:
    """Create a SystemdUserService instance with temporary home directory"""
    systemd_dir = temporary_home / ".config" / "systemd" / "user"
    return SystemdUserService(user_systemd_dir=systemd_dir)


class TestSystemdUserService:
    def test_service_name_generation(self, systemd_service: SystemdUserService) -> None:
        """Test service name generation from name"""
        name = "test-service"
        service_name = systemd_service._service_name(name)

        assert service_name == "service-runner-test-service"

    def test_unit_file_path(
        self, systemd_service: SystemdUserService, temporary_home: Path
    ) -> None:
        """Test unit file path generation"""
        name = "test-service"
        unit_file = systemd_service._unit_file_path(name)

        expected_dir = temporary_home / ".config" / "systemd" / "user"
        assert unit_file.parent == expected_dir
        assert unit_file.suffix == ".service"
        assert unit_file.name == "service-runner-test-service.service"

    def test_create_unit_file(
        self, systemd_service: SystemdUserService, temporary_home: Path
    ) -> None:
        """Test systemd unit file creation"""
        name = "test-service"
        command = ["python3", "-c", "print('test')"]
        working_dir = temporary_home
        env_vars = {"TEST_VAR": "test_value", "ANOTHER": "value"}
        description = "Test service"

        unit_file = systemd_service._create_unit_file(
            name, command, working_dir, env_vars, description
        )

        assert unit_file.exists()
        content = unit_file.read_text()

        # Check basic structure
        assert "[Unit]" in content
        assert "[Service]" in content

        # Check specific values
        assert f'Description="{description}"' in content
        assert f"WorkingDirectory={working_dir}" in content
        assert "Environment=TEST_VAR=test_value" in content
        assert "Environment=ANOTHER=value" in content

    def test_create_unit_file_with_spaces(
        self, systemd_service: SystemdUserService
    ) -> None:
        """Test unit file creation with commands containing spaces"""
        name = "test-service"
        command = ["python3", "-c", "print('hello world')"]

        unit_file = systemd_service._create_unit_file(name, command)
        content = unit_file.read_text()
        executable = shutil.which(command[0])
        expect = f"ExecStart={executable} -c print('hello world')"
        # Should properly escape arguments with spaces
        assert expect in content

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_run_systemctl(
        self, mock_run: MagicMock, systemd_service: SystemdUserService
    ) -> None:
        """Test systemctl command execution"""
        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = "active"
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        result = systemd_service._run_systemctl("status", "test-service")

        mock_run.assert_called_once()
        assert result.returncode == 0

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_get_status_running(
        self, mock_run: MagicMock, systemd_service: SystemdUserService
    ) -> None:
        """Test status detection for running service"""
        # Mock unit file existence
        name = "test-service"
        unit_file = systemd_service._unit_file_path(name)
        unit_file.parent.mkdir(parents=True, exist_ok=True)
        unit_file.write_text("[Unit]\nDescription=test\n[Service]\nExecStart=echo test")

        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = "active"
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        status = systemd_service.get_status(name)
        assert status == "running"

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_get_status_stopped(
        self, mock_run: MagicMock, systemd_service: SystemdUserService
    ) -> None:
        """Test status detection for stopped service"""
        # Mock unit file existence
        name = "test-service"
        unit_file = systemd_service._unit_file_path(name)
        unit_file.parent.mkdir(parents=True, exist_ok=True)
        unit_file.write_text("[Unit]\nDescription=test\n[Service]\nExecStart=echo test")

        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = "inactive"
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        status = systemd_service.get_status(name)
        assert status == "stopped"

    def test_get_status_unknown_no_unit_file(
        self, systemd_service: SystemdUserService
    ) -> None:
        """Test status detection when no unit file exists"""
        name = "nonexistent"

        status = systemd_service.get_status(name)
        assert status == "unknown"


class TestServiceRunner:
    def test_empty_name_raises_error(self, service_runner: SystemdUserService) -> None:
        """Test that empty service name raises ClanError"""
        with pytest.raises(ClanError, match="Service name cannot be empty"):
            service_runner.start_service("", ["echo", "test"])

    def test_empty_command_raises_error(
        self, service_runner: SystemdUserService
    ) -> None:
        """Test that empty command raises ClanError"""
        with pytest.raises(ClanError, match="Command cannot be empty"):
            service_runner.start_service("test-service", [])

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_start_service_mocked(
        self, mock_run: MagicMock, service_runner: SystemdUserService
    ) -> None:
        """Test service start with mocked systemctl calls"""
        # Mock successful systemctl calls
        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = ""
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        name = "test-service"
        command = ["echo", "test"]
        service_name = service_runner.start_service(
            name, command, description="Test service"
        )

        assert service_name == name

        # Verify systemctl calls were made
        assert mock_run.call_count >= 2  # At least daemon-reload, enable, start

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_stop_service_mocked(
        self, mock_run: MagicMock, service_runner: SystemdUserService
    ) -> None:
        """Test service stop with mocked systemctl calls"""
        # First create a unit file
        name = "test-service"
        command = ["echo", "test"]
        unit_file = service_runner._create_unit_file(name, command)

        # Mock successful systemctl calls
        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = ""
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        success = service_runner.stop_service(name)
        assert success is True

        # Check unit file was removed
        assert not unit_file.exists()

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_restart_service_mocked(
        self, mock_run: MagicMock, service_runner: SystemdUserService
    ) -> None:
        """Test service restart with mocked systemctl calls"""
        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = ""
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        name = "test-service"
        success = service_runner.restart_service(name)

        assert success is True

    @patch("clan_lib.service_runner.systemd_user.run")
    def test_logs_service_mocked(
        self, mock_run: MagicMock, service_runner: SystemdUserService
    ) -> None:
        """Test getting service logs with mocked journalctl"""
        expected_logs = "Test log output\nAnother log line"
        mock_cmd_out = MagicMock()
        mock_cmd_out.returncode = 0
        mock_cmd_out.stdout = expected_logs
        mock_cmd_out.stderr = ""
        mock_run.return_value = mock_cmd_out

        name = "test-service"
        logs = service_runner.get_service_logs(name, lines=25)

        assert logs == expected_logs
        mock_run.assert_called_once()
        # Check journalctl command structure
        call_args = mock_run.call_args[0][0]
        assert "journalctl" in call_args
        assert "--user" in call_args
        assert "-n" in call_args
        assert "25" in call_args

    def test_list_services_empty(self, service_runner: SystemdUserService) -> None:
        """Test listing services when none exist"""
        services = service_runner.list_running_services()
        assert services == []

    def test_list_services_with_unit_files(
        self, service_runner: SystemdUserService
    ) -> None:
        """Test listing services when unit files exist"""
        # Create some mock unit files
        systemd_dir = service_runner.user_systemd_dir

        unit1 = systemd_dir / "service-runner-test1.service"
        unit1.write_text("""[Unit]
Description=Test Service 1

[Service]
ExecStart=echo test1

[Install]
WantedBy=default.target
""")

        unit2 = systemd_dir / "service-runner-test2.service"
        unit2.write_text("""[Unit]
Description=Test Service 2

[Service]
ExecStart=python3 -c "print('test')"

[Install]
WantedBy=default.target
""")

        with patch("clan_lib.service_runner.systemd_user.run") as mock_run:
            mock_cmd_out = MagicMock()
            mock_cmd_out.returncode = 0
            mock_cmd_out.stdout = "inactive"
            mock_cmd_out.stderr = ""
            mock_run.return_value = mock_cmd_out

            services = service_runner.list_running_services()

            assert len(services) == 2

            service_names = [s["service_name"] for s in services]
            assert "service-runner-test1" in service_names
            assert "service-runner-test2" in service_names

            # Check command extraction
            commands = [s["command"] for s in services]
            assert "echo test1" in commands
            assert "python3 -c \"print('test')\"" in commands
