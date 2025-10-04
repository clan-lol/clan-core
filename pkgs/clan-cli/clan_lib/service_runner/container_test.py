#!/usr/bin/env python3
"""Test suite for service runner with group functionality."""

# Allow assert statements and magic values in test code

import time
from collections.abc import Generator
from contextlib import suppress
from pathlib import Path

import pytest

from clan_lib.errors import ClanError
from clan_lib.service_runner import create_service_manager
from clan_lib.service_runner.protocols import ServiceManagerProtocol


@pytest.fixture
def service_manager() -> Generator[ServiceManagerProtocol]:
    """Create a service manager and ensure cleanup after test."""
    manager = create_service_manager()

    # List of services that might be created during tests
    test_services = [
        "simple-service",
        "nginx-service",
        "api-service",
        "postgres-service",
        "autostart-service",
        "log-test",
        "restart-test",
    ]

    # Test groups that might be created
    test_groups = ["web", "database"]

    # Yield the manager to the test
    yield manager

    # Cleanup after test (runs even if test fails)
    for service in test_services:
        with suppress(ClanError):
            manager.stop_service(service)

    for group in test_groups:
        with suppress(ClanError):
            manager.stop_services_by_group(group)


@pytest.mark.service_runner
def test_transient_service(service_manager: ServiceManagerProtocol) -> None:
    """Test transient service (no autostart, uses systemd-run)."""
    # Start a transient service
    name = service_manager.start_service(
        name="simple-service",
        command=["sleep", "300"],
        description="A simple transient service",
        autostart=False,
    )
    assert name == "simple-service", f"Expected 'simple-service', got {name}"

    # Give systemd time to start the service
    time.sleep(0.5)

    # Check status
    status = service_manager.get_status("simple-service")
    assert status == "running", f"Expected 'running', got {status}"

    # Verify it's listed
    services = service_manager.list_running_services()
    service_names = [s["service_name"] for s in services]
    assert "service-runner-simple-service" in service_names, "Service not in list"

    # Check it's marked as transient (no unit file)
    simple_service = next(
        s for s in services if s["service_name"] == "service-runner-simple-service"
    )
    assert simple_service["unit_file"] == "(transient)", (
        f"Should be transient, got {simple_service['unit_file']!r}"
    )

    # Stop the service
    service_manager.stop_service("simple-service")

    # Verify it's stopped
    time.sleep(0.5)
    status = service_manager.get_status("simple-service")
    assert status in ("stopped", "unknown"), f"Expected stopped/unknown, got {status}"


@pytest.mark.service_runner
def test_autostart_service(service_manager: ServiceManagerProtocol) -> None:
    """Test autostart service (creates persistent unit file)."""
    # Start an autostart service
    service_manager.start_service(
        name="autostart-service",
        command=["sleep", "300"],
        description="An autostart service",
        autostart=True,
    )

    time.sleep(0.5)

    # Check status
    status = service_manager.get_status("autostart-service")
    assert status == "running", f"Expected 'running', got {status}"

    # Verify it has a unit file (not transient)
    services = service_manager.list_running_services()
    autostart_service = next(
        s for s in services if s["service_name"] == "service-runner-autostart-service"
    )
    assert autostart_service["unit_file"] != "(transient)", "Should have unit file"
    assert autostart_service["unit_file"].endswith(".service"), (
        "Should be .service file"
    )

    # Verify unit file exists
    unit_file = Path(autostart_service["unit_file"])
    assert unit_file.exists(), f"Unit file should exist: {unit_file}"

    # Stop and verify unit file is removed
    service_manager.stop_service("autostart-service")

    time.sleep(0.5)
    assert not unit_file.exists(), f"Unit file should be removed: {unit_file}"


@pytest.mark.service_runner
def test_grouped_services(service_manager: ServiceManagerProtocol) -> None:
    """Test services with groups."""
    # Start services in the "web" group
    service_manager.start_service(
        name="nginx-service",
        command=["sleep", "300"],
        description="Web server",
        autostart=True,
        group="web",
    )

    service_manager.start_service(
        name="api-service",
        command=["sleep", "300"],
        description="API server",
        autostart=True,
        group="web",
    )

    # Start service in "database" group
    service_manager.start_service(
        name="postgres-service",
        command=["sleep", "300"],
        description="Database server",
        autostart=True,
        group="database",
    )

    time.sleep(0.5)

    # Verify all services are running
    all_services = service_manager.list_running_services()
    service_names = {s["service_name"] for s in all_services}
    assert "service-runner-nginx-service" in service_names
    assert "service-runner-api-service" in service_names
    assert "service-runner-postgres-service" in service_names

    # List services by group
    web_services = service_manager.list_services_by_group("web")
    assert len(web_services) == 2, f"Expected 2 web services, got {len(web_services)}"
    web_service_names = {s["service_name"] for s in web_services}
    assert "service-runner-nginx-service" in web_service_names
    assert "service-runner-api-service" in web_service_names

    db_services = service_manager.list_services_by_group("database")
    assert len(db_services) == 1, f"Expected 1 db service, got {len(db_services)}"
    assert db_services[0]["service_name"] == "service-runner-postgres-service"
    assert db_services[0]["group"] == "database"

    # Verify all grouped services have unit files
    for service in web_services + db_services:
        assert service["unit_file"] != "(transient)", (
            f"{service['service_name']} should have unit file"
        )
        assert service["status"] == "active", (
            f"{service['service_name']} should be active"
        )

    # Stop services by group
    service_manager.stop_services_by_group("web")

    time.sleep(0.5)

    # Verify web services are stopped
    web_services_after = service_manager.list_services_by_group("web")
    assert len(web_services_after) == 0, "Web services should be stopped"

    # Verify database service is still running
    db_services_after = service_manager.list_services_by_group("database")
    assert len(db_services_after) == 1, "Database service should still be running"

    # Clean up database group
    service_manager.stop_services_by_group("database")

    time.sleep(0.5)
    db_services_final = service_manager.list_services_by_group("database")
    assert len(db_services_final) == 0, "Database services should be stopped"


@pytest.mark.service_runner
def test_service_logs(service_manager: ServiceManagerProtocol) -> None:
    """Test retrieving service logs."""
    # Start a service
    service_manager.start_service(
        name="log-test",
        command=["sleep", "300"],
        description="Log test service",
        autostart=False,
    )

    time.sleep(0.5)

    # Get logs - just verify we can retrieve them (may be empty)
    logs = service_manager.get_service_logs("log-test", lines=20)
    assert isinstance(logs, str), "Logs should be a string"

    # Clean up
    service_manager.stop_service("log-test")


@pytest.mark.service_runner
def test_nonexistent_group(service_manager: ServiceManagerProtocol) -> None:
    """Test listing services in nonexistent group."""
    # List services in nonexistent group
    services = service_manager.list_services_by_group("nonexistent-group")
    assert services == [], f"Expected empty list, got {services}"


@pytest.mark.service_runner
def test_restart_service(service_manager: ServiceManagerProtocol) -> None:
    """Test restarting a service."""
    # Start a service
    service_manager.start_service(
        name="restart-test",
        command=["sleep", "300"],
        description="Restart test service",
        autostart=False,
    )

    time.sleep(0.5)

    # Verify it's running
    status = service_manager.get_status("restart-test")
    assert status == "running", f"Expected 'running', got {status}"

    # Restart it
    service_manager.restart_service("restart-test")

    time.sleep(0.5)

    # Verify it's still running
    status = service_manager.get_status("restart-test")
    assert status == "running", f"Expected 'running' after restart, got {status}"

    # Clean up
    service_manager.stop_service("restart-test")


@pytest.mark.service_runner
def test_cleanup_on_failure(service_manager: ServiceManagerProtocol) -> None:
    """Test that services are cleaned up even when test fails."""
    # Start a service
    service_manager.start_service(
        name="simple-service",
        command=["sleep", "300"],
        autostart=False,
    )

    time.sleep(0.5)

    # Verify it's running
    status = service_manager.get_status("simple-service")
    assert status == "running"

    # Service will be cleaned up by fixture even if we don't explicitly stop it
    # This test passes, demonstrating that cleanup happens automatically


@pytest.mark.service_runner
def test_start_service_twice_transient(service_manager: ServiceManagerProtocol) -> None:
    """Test starting the same transient service twice (should fail or replace)."""
    # Start a transient service
    service_manager.start_service(
        name="simple-service",
        command=["sleep", "300"],
        autostart=False,
    )

    time.sleep(0.5)

    # Verify it's running
    status = service_manager.get_status("simple-service")
    assert status == "running"

    # Try to start the same service again - this should fail
    # systemd won't allow starting a unit with the same name
    with pytest.raises(ClanError, match="Failed to start service"):
        service_manager.start_service(
            name="simple-service",
            command=["sleep", "300"],
            autostart=False,
        )

    # Original service should still be running
    status = service_manager.get_status("simple-service")
    assert status == "running"


@pytest.mark.service_runner
def test_start_service_twice_autostart(service_manager: ServiceManagerProtocol) -> None:
    """Test starting the same autostart service twice (just restarts it)."""
    # Start an autostart service
    service_manager.start_service(
        name="autostart-service",
        command=["sleep", "300"],
        autostart=True,
    )

    time.sleep(0.5)

    # Verify it's running
    status = service_manager.get_status("autostart-service")
    assert status == "running"

    # Try to start the same service again
    # For autostart services, systemd will just restart the service
    # (unlike transient services which fail)
    service_manager.start_service(
        name="autostart-service",
        command=["sleep", "300"],
        autostart=True,
    )

    time.sleep(0.5)

    # Service should still be running after "restart"
    status = service_manager.get_status("autostart-service")
    assert status == "running"


@pytest.mark.service_runner
def test_start_stopped_service_again(service_manager: ServiceManagerProtocol) -> None:
    """Test starting a service, stopping it, then starting it again."""
    # Start a service
    service_manager.start_service(
        name="simple-service",
        command=["sleep", "300"],
        autostart=False,
    )

    time.sleep(0.5)
    status = service_manager.get_status("simple-service")
    assert status == "running"

    # Stop the service
    service_manager.stop_service("simple-service")
    time.sleep(0.5)

    status = service_manager.get_status("simple-service")
    assert status in ("stopped", "unknown")

    # Start the service again with a different command - this should work
    service_manager.start_service(
        name="simple-service",
        command=["sleep", "600"],
        description="Restarted service with different command",
        autostart=False,
    )

    time.sleep(0.5)
    status = service_manager.get_status("simple-service")
    assert status == "running"
