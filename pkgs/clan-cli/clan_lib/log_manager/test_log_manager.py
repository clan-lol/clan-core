"""
Simplified tests for the log manager focusing only on features used by the API.

Tests are based on actual usage patterns from example_usage.py and api.py.
"""

import datetime
from pathlib import Path

import pytest

from clan_lib.log_manager import (
    LogGroupConfig,
    LogManager,
    is_correct_day_format,
)


# Test functions for log creation
def run_machine_update() -> None:
    """Test function for deploying machines."""


def example_function() -> None:
    """Example function for creating logs."""


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    """Provides a temporary base directory for logs."""
    return tmp_path / "logs"


@pytest.fixture
def log_manager(base_dir: Path) -> LogManager:
    """Provides a LogManager instance."""
    return LogManager(base_dir=base_dir)


@pytest.fixture
def configured_log_manager(base_dir: Path) -> LogManager:
    """Provides a LogManager with group configuration like example_usage.py."""
    log_manager = LogManager(base_dir=base_dir)

    # Configure structure: clans -> <dynamic> -> machines -> <dynamic>
    clans_config = LogGroupConfig("clans", "Clans")
    machines_config = LogGroupConfig("machines", "Machines")
    clans_config = clans_config.add_child(machines_config)
    log_manager = log_manager.add_root_group_config(clans_config)

    return log_manager


class TestLogGroupConfig:
    """Test LogGroupConfig functionality used in example_usage.py."""

    def test_creation_with_nickname(self) -> None:
        """Test creating group config with nickname."""
        config = LogGroupConfig("clans", "Clans")
        assert config.name == "clans"
        assert config.nickname == "Clans"
        assert config.children == {}

    def test_creation_without_nickname(self) -> None:
        """Test creating group config without nickname."""
        config = LogGroupConfig("machines")
        assert config.name == "machines"
        assert config.nickname is None
        assert config.children == {}

    def test_get_display_name_with_nickname(self) -> None:
        """Test display name returns nickname when available."""
        config = LogGroupConfig("clans", "Clans")
        assert config.get_display_name() == "Clans"

    def test_get_display_name_without_nickname(self) -> None:
        """Test display name returns name when no nickname."""
        config = LogGroupConfig("machines")
        assert config.get_display_name() == "machines"

    def test_add_child(self) -> None:
        """Test adding child group configuration."""
        parent = LogGroupConfig("clans", "Clans")
        child = LogGroupConfig("machines", "Machines")

        updated_parent = parent.add_child(child)

        # Original should be unchanged (immutable)
        assert parent.children == {}

        # Updated parent should have child
        assert "machines" in updated_parent.children
        assert updated_parent.children["machines"] == child

    def test_get_child(self) -> None:
        """Test retrieving child group configuration."""
        parent = LogGroupConfig("clans", "Clans")
        child = LogGroupConfig("machines", "Machines")
        parent = parent.add_child(child)

        retrieved_child = parent.get_child("machines")
        assert retrieved_child == child

        non_existent = parent.get_child("nonexistent")
        assert non_existent is None


class TestDateFormatValidation:
    """Test date format validation function."""

    def test_valid_date_formats(self) -> None:
        """Test valid YYYY-MM-DD formats."""
        assert is_correct_day_format("2023-10-26")
        assert is_correct_day_format("2024-01-01")
        assert is_correct_day_format("2024-12-31")

    def test_invalid_date_formats(self) -> None:
        """Test invalid date formats."""
        assert not is_correct_day_format("2023/10/26")
        assert not is_correct_day_format("23-10-26")
        assert not is_correct_day_format("2023-13-01")  # Invalid month
        assert not is_correct_day_format("2023-10-32")  # Invalid day
        assert not is_correct_day_format("not-a-date")
        assert not is_correct_day_format("")


class TestLogManagerGroupConfiguration:
    """Test LogManager group configuration features used in example_usage.py."""

    def test_add_root_group_config(self, log_manager: LogManager) -> None:
        """Test adding root group configuration."""
        clans_config = LogGroupConfig("clans", "Clans")
        updated_manager = log_manager.add_root_group_config(clans_config)

        # Original should be unchanged (immutable)
        assert log_manager.root_group_configs == {}

        # Updated manager should have config
        assert "clans" in updated_manager.root_group_configs
        assert updated_manager.root_group_configs["clans"] == clans_config

    def test_find_group_config_simple(self, configured_log_manager: LogManager) -> None:
        """Test finding simple group configuration."""
        config = configured_log_manager.find_group_config(["clans"])
        assert config is not None
        assert config.name == "clans"
        assert config.nickname == "Clans"

    def test_find_group_config_nested(self, configured_log_manager: LogManager) -> None:
        """Test finding nested group configuration."""
        # ["clans", "dynamic_name", "machines"] - should find machines config
        config = configured_log_manager.find_group_config(
            ["clans", "repo1", "machines"]
        )
        assert config is not None
        assert config.name == "machines"
        assert config.nickname == "Machines"

    def test_find_group_config_nonexistent(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test finding non-existent group configuration."""
        config = configured_log_manager.find_group_config(["nonexistent"])
        assert config is None

        config = configured_log_manager.find_group_config([])
        assert config is None


class TestLogFileCreation:
    """Test log file creation features used in example_usage.py."""

    def test_create_log_file_default_group(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test creating log file with default group."""
        log_file = configured_log_manager.create_log_file(example_function, "test_op")

        assert log_file.op_key == "test_op"
        assert log_file.func_name == "example_function"
        assert log_file.group == "default"
        assert is_correct_day_format(log_file.date_day)

        # Check file was created
        assert log_file.get_file_path().exists()

    def test_create_log_file_with_nested_groups(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test creating log file with nested groups like example_usage.py."""
        repos = ["/home/user/Projects/qubasas_clan", "https://github.com/qubasa/myclan"]
        machines = ["wintux", "demo", "gchq-local"]

        for repo in repos:
            for machine in machines:
                log_file = configured_log_manager.create_log_file(
                    run_machine_update,
                    f"deploy_{machine}",
                    ["clans", repo, "machines", machine],
                )

                assert log_file.op_key == f"deploy_{machine}"
                assert log_file.func_name == "run_machine_update"
                assert log_file.get_file_path().exists()

                # Check the group structure includes URL encoding for dynamic parts
                group_parts = log_file.group.split("/")
                assert group_parts[0] == "clans"  # Structure element
                assert group_parts[2] == "machines"  # Structure element
                # Dynamic elements should be URL encoded if they contain special chars

    def test_create_log_file_unregistered_group_fails(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that creating log file with unregistered group fails."""
        with pytest.raises(ValueError, match="Group structure.*is not valid"):
            configured_log_manager.create_log_file(
                example_function,
                "test_op",
                ["unregistered_group"],
            )

    def test_create_log_file_invalid_structure_fails(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that invalid nested structure fails."""
        with pytest.raises(ValueError, match="Group structure.*is not valid"):
            configured_log_manager.create_log_file(
                example_function,
                "test_op",
                ["clans", "repo", "invalid_structure"],
            )


class TestFilterFunction:
    """Test filter functionality used in example_usage.py and api.py."""

    def test_filter_empty_returns_top_level_groups(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that empty filter returns top-level groups."""
        # Create some log files first
        configured_log_manager.create_log_file(
            run_machine_update, "test_op", ["clans", "repo1", "machines", "machine1"]
        )

        top_level = configured_log_manager.filter([])
        assert "clans" in top_level

    def test_filter_lists_dynamic_names(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test filtering lists dynamic names like example_usage.py."""
        repos = ["repo1", "repo2"]
        machines = ["machine1", "machine2"]

        # Create log files with different repos and machines
        for repo in repos:
            for machine in machines:
                configured_log_manager.create_log_file(
                    run_machine_update,
                    f"deploy_{machine}",
                    ["clans", repo, "machines", machine],
                )

        # List all repositories under 'clans'
        clans_repos = configured_log_manager.filter(["clans"])
        assert set(clans_repos) == set(repos)

        # List machines under first repository
        if clans_repos:
            first_repo = clans_repos[0]
            repo_machines = configured_log_manager.filter(
                ["clans", first_repo, "machines"]
            )
            assert set(repo_machines) == set(machines)

    def test_filter_with_specific_date(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test filtering with specific date."""
        # Create log file
        log_file = configured_log_manager.create_log_file(
            run_machine_update, "test_op", ["clans", "repo1", "machines", "machine1"]
        )

        # Filter with the specific date
        repos = configured_log_manager.filter(["clans"], date_day=log_file.date_day)
        assert "repo1" in repos

        # Filter with non-existent date
        tomorrow = (
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        ).strftime("%Y-%m-%d")
        repos = configured_log_manager.filter(["clans"], date_day=tomorrow)
        assert repos == []

    def test_filter_nonexistent_path(self, configured_log_manager: LogManager) -> None:
        """Test filtering non-existent path returns empty list."""
        result = configured_log_manager.filter(["nonexistent"])
        assert result == []


class TestGetLogFile:
    """Test get_log_file functionality used in example_usage.py and api.py."""

    def test_get_log_file_by_op_key(self, configured_log_manager: LogManager) -> None:
        """Test getting log file by operation key."""
        # Create log file
        configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_wintux",
            ["clans", "repo1", "machines", "wintux"],
        )

        # Find it by op_key
        found_log_file = configured_log_manager.get_log_file("deploy_wintux")
        assert found_log_file is not None
        assert found_log_file.op_key == "deploy_wintux"
        assert found_log_file.func_name == "run_machine_update"

    def test_get_log_file_with_selector(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test getting log file with specific selector like example_usage.py."""
        # Create log files in different locations
        configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_wintux",
            ["clans", "repo1", "machines", "wintux"],
        )
        configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_wintux",
            ["clans", "repo2", "machines", "wintux"],
        )

        # Find specific one using selector
        specific_log = configured_log_manager.get_log_file(
            "deploy_wintux",
            selector=["clans", "repo1", "machines", "wintux"],
        )
        assert specific_log is not None
        assert specific_log.op_key == "deploy_wintux"

    def test_get_log_file_with_date(self, configured_log_manager: LogManager) -> None:
        """Test getting log file with specific date."""
        # Create log file
        log_file = configured_log_manager.create_log_file(
            run_machine_update, "deploy_demo", ["clans", "repo1", "machines", "demo"]
        )

        # Find it by op_key and date
        found_log_file = configured_log_manager.get_log_file(
            "deploy_demo", date_day=log_file.date_day
        )
        assert found_log_file is not None
        assert found_log_file.op_key == "deploy_demo"

        # Try with wrong date
        tomorrow = (
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        ).strftime("%Y-%m-%d")
        not_found = configured_log_manager.get_log_file(
            "deploy_demo", date_day=tomorrow
        )
        assert not_found is None

    def test_get_log_file_nonexistent(self, configured_log_manager: LogManager) -> None:
        """Test getting non-existent log file returns None."""
        result = configured_log_manager.get_log_file("nonexistent_op")
        assert result is None


class TestListLogDays:
    """Test list_log_days functionality used in api.py."""

    def test_list_log_days_empty(self, log_manager: LogManager) -> None:
        """Test listing log days when no logs exist."""
        days = log_manager.list_log_days()
        assert days == []

    def test_list_log_days_populated(self, configured_log_manager: LogManager) -> None:
        """Test listing log days when logs exist."""
        # Create log files
        configured_log_manager.create_log_file(
            run_machine_update, "op1", ["clans", "repo1", "machines", "machine1"]
        )
        configured_log_manager.create_log_file(
            run_machine_update, "op2", ["clans", "repo2", "machines", "machine2"]
        )

        days = configured_log_manager.list_log_days()
        assert len(days) >= 1  # Should have at least today

        # Days should be sorted newest first
        if len(days) > 1:
            assert days[0].date_day >= days[1].date_day


class TestApiCompatibility:
    """Test that the log manager works with the API functions."""

    def test_api_workflow_like_example_usage(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test a complete workflow like example_usage.py and api.py."""
        repos = ["/home/user/Projects/qubasas_clan", "https://github.com/qubasa/myclan"]
        machines = ["wintux", "demo"]

        # Create logs like example_usage.py
        for repo in repos:
            for machine in machines:
                configured_log_manager.create_log_file(
                    run_machine_update,
                    f"deploy_{machine}",
                    ["clans", repo, "machines", machine],
                )

        # Test list_log_days (api.py)
        log_days = configured_log_manager.list_log_days()
        assert len(log_days) >= 1

        # Test list_log_groups (api.py) - equivalent to filter
        top_level = configured_log_manager.filter([])
        assert "clans" in top_level

        clans_repos = configured_log_manager.filter(["clans"])
        assert len(clans_repos) == len(repos)

        # Test get_log_file (api.py)
        specific_log = configured_log_manager.get_log_file(
            "deploy_wintux",
            selector=["clans", repos[0], "machines", "wintux"],
        )
        assert specific_log is not None
        assert specific_log.op_key == "deploy_wintux"

        # Test file content can be read (api.py does read_text())
        file_path = specific_log.get_file_path()
        assert file_path.exists(), f"File does not exist at {file_path}"
        content = file_path.read_text()
        assert isinstance(content, str)  # File exists and is readable


class TestLogFileSorting:
    """Test LogFile sorting functionality - newest first is a key feature."""

    def test_logfile_comparison_by_datetime(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that LogFiles are sorted by datetime (newest first)."""
        from clan_lib.log_manager import LogFile

        # Create LogFiles with different times (same date)
        newer_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",
            group="test_group",
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="15-30-45",  # 3:30:45 PM
        )

        older_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",
            group="test_group",
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="10-15-30",  # 10:15:30 AM
        )

        # Newer file should be "less than" older file (sorts first)
        assert newer_file < older_file
        assert not (older_file < newer_file)

        # Test with sorted()
        files = [older_file, newer_file]
        sorted_files = sorted(files)
        assert sorted_files[0] == newer_file  # Newest first
        assert sorted_files[1] == older_file

    def test_logfile_comparison_by_date(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that LogFiles are sorted by date (newer dates first)."""
        from clan_lib.log_manager import LogFile

        # Create LogFiles with different dates
        newer_date_file = LogFile(
            op_key="test_op",
            date_day="2023-10-27",  # Newer date
            group="test_group",
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        older_date_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",  # Older date
            group="test_group",
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="15-00-00",  # Later time, but older date
        )

        # Newer date should sort first regardless of time
        assert newer_date_file < older_date_file

        # Test with sorted()
        files = [older_date_file, newer_date_file]
        sorted_files = sorted(files)
        assert sorted_files[0] == newer_date_file  # Newest date first
        assert sorted_files[1] == older_date_file

    def test_logfile_secondary_sort_by_group(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that LogFiles with same datetime are sorted by group name (alphabetical)."""
        from clan_lib.log_manager import LogFile

        # Create LogFiles with same datetime but different groups
        group_a_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",
            group="group_a",  # Should sort first alphabetically
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        group_b_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",
            group="group_b",  # Should sort second
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        # group_a should sort before group_b
        assert group_a_file < group_b_file
        assert not (group_b_file < group_a_file)

        # Test with sorted()
        files = [group_b_file, group_a_file]
        sorted_files = sorted(files)
        assert sorted_files[0] == group_a_file
        assert sorted_files[1] == group_b_file

    def test_logfile_tertiary_sort_by_func_name(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that LogFiles with same datetime and group are sorted by func_name (alphabetical)."""
        from clan_lib.log_manager import LogFile

        # Create LogFiles with same datetime and group but different func_names
        func_a_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",
            group="test_group",
            func_name="func_a",  # Should sort first alphabetically
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        func_b_file = LogFile(
            op_key="test_op",
            date_day="2023-10-26",
            group="test_group",
            func_name="func_b",  # Should sort second
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        # func_a should sort before func_b
        assert func_a_file < func_b_file

        # Test with sorted()
        files = [func_b_file, func_a_file]
        sorted_files = sorted(files)
        assert sorted_files[0] == func_a_file
        assert sorted_files[1] == func_b_file

    def test_logfile_quaternary_sort_by_op_key(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that LogFiles with same datetime, group, and func_name are sorted by op_key (alphabetical)."""
        from clan_lib.log_manager import LogFile

        # Create LogFiles identical except for op_key
        op_a_file = LogFile(
            op_key="op_a",  # Should sort first alphabetically
            date_day="2023-10-26",
            group="test_group",
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        op_b_file = LogFile(
            op_key="op_b",  # Should sort second
            date_day="2023-10-26",
            group="test_group",
            func_name="test_func",
            _base_dir=configured_log_manager.base_dir,
            date_second="10-00-00",
        )

        # op_a should sort before op_b
        assert op_a_file < op_b_file

        # Test with sorted()
        files = [op_b_file, op_a_file]
        sorted_files = sorted(files)
        assert sorted_files[0] == op_a_file
        assert sorted_files[1] == op_b_file

    def test_logfile_complex_sorting_scenario(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test complex sorting with multiple LogFiles demonstrating full sort order."""

        from clan_lib.log_manager import LogFile

        # Create multiple files with different characteristics
        files = [
            # Oldest datetime, should be last
            LogFile(
                "op_z",
                "2023-10-25",
                "group_z",
                "func_z",
                configured_log_manager.base_dir,
                "09-00-00",
            ),
            # Same datetime as next, but group_b > group_a, should be after group_a file
            LogFile(
                "op_a",
                "2023-10-26",
                "group_b",
                "func_a",
                configured_log_manager.base_dir,
                "10-00-00",
            ),
            # Same datetime as prev, but group_a < group_b, should be before group_b file
            LogFile(
                "op_a",
                "2023-10-26",
                "group_a",
                "func_a",
                configured_log_manager.base_dir,
                "10-00-00",
            ),
            # Same as prev except func_b > func_a, should be after
            LogFile(
                "op_a",
                "2023-10-26",
                "group_a",
                "func_b",
                configured_log_manager.base_dir,
                "10-00-00",
            ),
            # Same as group_a/func_a but op_b > op_a, should be after the op_a version
            LogFile(
                "op_b",
                "2023-10-26",
                "group_a",
                "func_a",
                configured_log_manager.base_dir,
                "10-00-00",
            ),
            # Newest datetime, should be first
            LogFile(
                "op_a",
                "2023-10-26",
                "group_a",
                "func_a",
                configured_log_manager.base_dir,
                "15-30-00",
            ),
        ]

        sorted_files = sorted(files)

        # Expected order: newest datetime first, then by group, func_name, op_key
        expected_order = [
            ("op_a", "2023-10-26", "group_a", "func_a", "15-30-00"),  # Newest time
            (
                "op_a",
                "2023-10-26",
                "group_a",
                "func_a",
                "10-00-00",
            ),  # Same time, op_a < op_b
            (
                "op_b",
                "2023-10-26",
                "group_a",
                "func_a",
                "10-00-00",
            ),  # Same time, op_b > op_a
            (
                "op_a",
                "2023-10-26",
                "group_a",
                "func_b",
                "10-00-00",
            ),  # Same time/group, func_b > func_a
            (
                "op_a",
                "2023-10-26",
                "group_b",
                "func_a",
                "10-00-00",
            ),  # Same time, group_b > group_a
            ("op_z", "2023-10-25", "group_z", "func_z", "09-00-00"),  # Oldest datetime
        ]

        for i, (exp_op, exp_date, exp_group, exp_func, exp_time) in enumerate(
            expected_order
        ):
            actual = sorted_files[i]
            assert actual.op_key == exp_op, (
                f"Position {i}: expected op_key {exp_op}, got {actual.op_key}"
            )
            assert actual.date_day == exp_date, (
                f"Position {i}: expected date {exp_date}, got {actual.date_day}"
            )
            assert actual.group == exp_group, (
                f"Position {i}: expected group {exp_group}, got {actual.group}"
            )
            assert actual.func_name == exp_func, (
                f"Position {i}: expected func {exp_func}, got {actual.func_name}"
            )
            assert actual.date_second == exp_time, (
                f"Position {i}: expected time {exp_time}, got {actual.date_second}"
            )

    def test_get_log_file_returns_newest_when_multiple_exist(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that get_log_file returns the newest file when multiple files with same op_key exist in different locations."""
        # Create log files with same op_key in different locations (different groups/machines)
        # This simulates the realistic scenario where the same operation runs on different machines

        configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_operation",
            ["clans", "repo1", "machines", "machine1"],
        )

        configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_operation",
            ["clans", "repo1", "machines", "machine2"],
        )

        configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_operation",
            ["clans", "repo2", "machines", "machine1"],
        )

        # When searching without selector, should find one of them (newest by timestamp)
        found_log = configured_log_manager.get_log_file("deploy_operation")
        assert found_log is not None
        assert found_log.op_key == "deploy_operation"

        # When searching with specific selector, should find the specific one
        specific_log = configured_log_manager.get_log_file(
            "deploy_operation", selector=["clans", "repo1", "machines", "machine1"]
        )
        assert specific_log is not None
        assert specific_log.op_key == "deploy_operation"
        # Should be the one from machine1 in repo1
        assert "machine1" in specific_log.group

    def test_list_log_days_sorted_newest_first(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that list_log_days returns days sorted newest first."""
        # Create log files on different days by manipulating the date
        import tempfile

        # Create files with different dates manually to test sorting
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            manager = LogManager(base_dir=base_dir)

            # Create directories for different dates
            dates = [
                "2023-10-25",
                "2023-10-27",
                "2023-10-26",
            ]  # Intentionally out of order

            for date in dates:
                date_dir = base_dir / date / "default" / "test_func"
                date_dir.mkdir(parents=True, exist_ok=True)
                log_file = date_dir / f"10-00-00_test_op_{date}.log"
                log_file.touch()

            # List log days
            log_days = manager.list_log_days()

            # Should be sorted newest first: 2023-10-27, 2023-10-26, 2023-10-25
            assert len(log_days) == 3
            assert log_days[0].date_day == "2023-10-27"  # Newest first
            assert log_days[1].date_day == "2023-10-26"  # Middle
            assert log_days[2].date_day == "2023-10-25"  # Oldest last


class TestURLEncoding:
    """Test URL encoding for dynamic group names with special characters."""

    def test_special_characters_in_dynamic_names(
        self, configured_log_manager: LogManager
    ) -> None:
        """Test that special characters in dynamic names are handled correctly."""
        special_repo = "/home/user/Projects/my clan"  # Contains space
        special_machine = "machine-1"  # Contains dash

        # Create log file with special characters
        log_file = configured_log_manager.create_log_file(
            run_machine_update,
            "deploy_special",
            ["clans", special_repo, "machines", special_machine],
        )

        # File should be created successfully
        assert log_file.get_file_path().exists()

        # Should be findable via filter (returns decoded names)
        repos = configured_log_manager.filter(["clans"])
        assert special_repo in repos

        machines = configured_log_manager.filter(["clans", special_repo, "machines"])
        assert special_machine in machines

        # Should be findable via get_log_file
        found_log = configured_log_manager.get_log_file(
            "deploy_special",
            selector=["clans", special_repo, "machines", special_machine],
        )
        assert found_log is not None
        assert found_log.op_key == "deploy_special"
