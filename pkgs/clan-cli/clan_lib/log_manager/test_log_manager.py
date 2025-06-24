# ruff: noqa: SLF001
import datetime
import logging  # For LogManager if not already imported
import urllib.parse
from pathlib import Path
from typing import Any  # Added Dict

import pytest

# Assuming your classes are in a file named 'log_manager_module.py'
# If they are in the same file as the tests, you don't need this relative import.
from clan_lib.log_manager import (
    LogDayDir,
    LogFile,
    LogFuncDir,
    LogGroupDir,
    LogManager,
    is_correct_day_format,
)


# Dummy function for LogManager.create_log_file
def sample_func_one() -> None:
    pass


def sample_func_two() -> None:
    pass


# --- Fixtures ---


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    """Provides a temporary base directory for logs."""
    return tmp_path / "logs"


@pytest.fixture
def log_manager(base_dir: Path) -> LogManager:
    """Provides a LogManager instance initialized with the temporary base_dir."""
    return LogManager(base_dir=base_dir)


@pytest.fixture
def populated_log_structure(
    log_manager: LogManager, base_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[LogManager, Path, dict[str, LogFile]]:
    """
    Creates a predefined log structure for testing listing and retrieval.
    Returns the log_manager, base_dir, and a dictionary of created LogFile objects.
    """
    created_files: dict[str, LogFile] = {}

    # Mock datetime.datetime.now for predictable file names
    class MockDateTime(datetime.datetime):
        _now_val = datetime.datetime(2023, 10, 26, 10, 0, 0, tzinfo=datetime.UTC)
        _delta = datetime.timedelta(seconds=0)

        @classmethod
        def now(cls: Any, tz: Any = None) -> "MockDateTime":
            current = cls._now_val + cls._delta
            cls._delta += datetime.timedelta(
                seconds=1, minutes=1
            )  # Increment for uniqueness
            return current

    monkeypatch.setattr(datetime, "datetime", MockDateTime)

    # Day 1: 2023-10-26
    # Group A, Func A
    lf1 = log_manager.create_log_file(
        sample_func_one, "op_key_A1", "group_a"
    )  # 10-00-00
    created_files["lf1"] = lf1
    lf2 = log_manager.create_log_file(
        sample_func_one, "op_key_A2", "group_a"
    )  # 10-01-01
    created_files["lf2"] = lf2
    # Group B, Func B
    lf3 = log_manager.create_log_file(
        sample_func_two, "op_key_B1", "group_b"
    )  # 10-02-02
    created_files["lf3"] = lf3

    # Day 2: 2023-10-27 (by advancing mock time enough)
    MockDateTime._now_val = datetime.datetime(
        2023, 10, 27, 12, 0, 0, tzinfo=datetime.UTC
    )
    MockDateTime._delta = datetime.timedelta(seconds=0)  # Reset delta for new day

    lf4 = log_manager.create_log_file(
        sample_func_one, "op_key_A3_day2", "group_a"
    )  # 12-00-00
    created_files["lf4"] = lf4

    # Create a malformed file and dir to test skipping
    malformed_day_dir = base_dir / "2023-13-01"  # Invalid date
    malformed_day_dir.mkdir(parents=True, exist_ok=True)
    (malformed_day_dir / "some_group" / "some_func").mkdir(parents=True, exist_ok=True)

    malformed_func_dir = (
        base_dir / "2023-10-26" / "group_a" / "malformed_func_dir_name!"
    )
    malformed_func_dir.mkdir(parents=True, exist_ok=True)

    malformed_log_file_dir = (
        base_dir / "2023-10-26" / "group_a" / sample_func_one.__name__
    )
    (malformed_log_file_dir / "badname.log").touch()
    (malformed_log_file_dir / "10-00-00_op_key.txt").touch()  # Wrong suffix

    return log_manager, base_dir, created_files


# --- Tests for is_correct_day_format ---


@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("2023-10-26", True),
        ("2024-01-01", True),
        ("2023-10-26X", False),
        ("2023/10/26", False),
        ("23-10-26", False),
        ("2023-13-01", False),  # Invalid month
        ("2023-02-30", False),  # Invalid day
        ("random-string", False),
        ("", False),
    ],
)
def test_is_correct_day_format(date_str: str, expected: bool) -> None:
    assert is_correct_day_format(date_str) == expected


# --- Tests for LogFile ---


class TestLogFile:
    def test_creation_valid(self, tmp_path: Path) -> None:
        lf = LogFile("op1", "2023-10-26", "test_group", "my_func", tmp_path, "10-20-30")
        assert lf.op_key == "op1"
        assert lf.date_day == "2023-10-26"
        assert lf.group == "test_group"
        assert lf.func_name == "my_func"
        assert lf._base_dir == tmp_path
        assert lf.date_second == "10-20-30"

    def test_creation_invalid_date_day(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in YYYY-MM-DD format"):
            LogFile("op1", "2023/10/26", "test_group", "my_func", tmp_path, "10-20-30")

    def test_creation_invalid_date_second(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in HH-MM-SS format"):
            LogFile("op1", "2023-10-26", "test_group", "my_func", tmp_path, "10:20:30")

    def test_datetime_obj(self, tmp_path: Path) -> None:
        lf = LogFile("op1", "2023-10-26", "test_group", "my_func", tmp_path, "10-20-30")
        expected_dt = datetime.datetime(2023, 10, 26, 10, 20, 30, tzinfo=datetime.UTC)
        assert lf._datetime_obj == expected_dt

    def test_from_path_valid(self, tmp_path: Path) -> None:
        base = tmp_path / "logs"
        file_path = (
            base / "2023-10-26" / "test_group" / "my_func" / "10-20-30_op_key_123.log"
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        lf = LogFile.from_path(file_path)
        assert lf.op_key == "op_key_123"
        assert lf.date_day == "2023-10-26"
        assert lf.group == "test_group"
        assert lf.func_name == "my_func"
        assert lf._base_dir == base
        assert lf.date_second == "10-20-30"

    def test_from_path_invalid_filename_format(self, tmp_path: Path) -> None:
        file_path = (
            tmp_path
            / "logs"
            / "2023-10-26"
            / "test_group"
            / "my_func"
            / "10-20-30-op_key_123.log"
        )  # Extra dash
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        with pytest.raises(ValueError, match="is not in HH-MM-SS format."):
            LogFile.from_path(file_path)

    def test_from_path_filename_no_op_key(self, tmp_path: Path) -> None:
        file_path = (
            tmp_path
            / "logs"
            / "2023-10-26"
            / "test_group"
            / "my_func"
            / "10-20-30_.log"
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        # This will result in op_key being ""
        lf = LogFile.from_path(file_path)
        assert lf.op_key == ""

    def test_get_file_path(self, tmp_path: Path) -> None:
        lf = LogFile("op1", "2023-10-26", "test_group", "my_func", tmp_path, "10-20-30")
        expected_path = (
            tmp_path / "2023-10-26" / "test_group" / "my_func" / "10-20-30_op1.log"
        )
        assert lf.get_file_path() == expected_path

    def test_equality(self, tmp_path: Path) -> None:
        lf1 = LogFile("op1", "2023-10-26", "group_a", "func_a", tmp_path, "10-00-00")
        lf2 = LogFile("op1", "2023-10-26", "group_a", "func_a", tmp_path, "10-00-00")
        lf3 = LogFile(
            "op2", "2023-10-26", "group_a", "func_a", tmp_path, "10-00-00"
        )  # Diff op_key
        lf4 = LogFile(
            "op1", "2023-10-26", "group_a", "func_a", tmp_path, "10-00-01"
        )  # Diff time
        lf5 = LogFile(
            "op1", "2023-10-26", "group_b", "func_a", tmp_path, "10-00-00"
        )  # Diff group
        assert lf1 == lf2
        assert lf1 != lf3
        assert lf1 != lf4
        assert lf1 != lf5
        assert lf1 != "not a logfile"

    def test_ordering(self, tmp_path: Path) -> None:
        # Newest datetime first
        lf_newest = LogFile("op", "2023-10-26", "group", "f", tmp_path, "10-00-01")
        lf_older = LogFile("op", "2023-10-26", "group", "f", tmp_path, "10-00-00")
        lf_oldest_d = LogFile("op", "2023-10-25", "group", "f", tmp_path, "12-00-00")

        # Same datetime, different group (alphabetical)
        lf_group_a = LogFile(
            "op", "2023-10-26", "group_a", "func", tmp_path, "10-00-00"
        )
        lf_group_b = LogFile(
            "op", "2023-10-26", "group_b", "func", tmp_path, "10-00-00"
        )

        # Same datetime, same group, different func_name (alphabetical)
        lf_func_a = LogFile("op", "2023-10-26", "group", "func_a", tmp_path, "10-00-00")
        lf_func_b = LogFile("op", "2023-10-26", "group", "func_b", tmp_path, "10-00-00")

        # Same datetime, same group, same func_name, different op_key (alphabetical)
        lf_op_a = LogFile("op_a", "2023-10-26", "group", "func_a", tmp_path, "10-00-00")
        lf_op_b = LogFile("op_b", "2023-10-26", "group", "func_a", tmp_path, "10-00-00")

        assert lf_newest < lf_older  # lf_newest is "less than" because it's newer
        assert lf_older < lf_oldest_d

        assert lf_group_a < lf_group_b
        assert not (lf_group_b < lf_group_a)

        assert lf_func_a < lf_func_b
        assert not (lf_func_b < lf_func_a)

        assert lf_op_a < lf_op_b
        assert not (lf_op_b < lf_op_a)

        # Test sorting with groups
        lf_ga_fa_op = LogFile(
            "op", "2023-10-26", "group_a", "func_a", tmp_path, "10-00-00"
        )
        lf_ga_fa_opa = LogFile(
            "op_a", "2023-10-26", "group_a", "func_a", tmp_path, "10-00-00"
        )
        lf_ga_fb_op = LogFile(
            "op", "2023-10-26", "group_a", "func_b", tmp_path, "10-00-00"
        )
        lf_gb_fa_op = LogFile(
            "op", "2023-10-26", "group_b", "func_a", tmp_path, "10-00-00"
        )
        lf_g_f_op1 = LogFile(
            "op", "2023-10-26", "group", "f", tmp_path, "10-00-01"
        )  # newest time
        lf_g_f_op0 = LogFile("op", "2023-10-26", "group", "f", tmp_path, "10-00-00")
        lf_old_day = LogFile("op", "2023-10-25", "group", "f", tmp_path, "12-00-00")

        files_with_groups = [
            lf_ga_fa_op,
            lf_ga_fa_opa,
            lf_ga_fb_op,
            lf_gb_fa_op,
            lf_g_f_op1,
            lf_g_f_op0,
            lf_old_day,
        ]
        sorted_with_groups = sorted(files_with_groups)

        # Expected order (newest first, then group, then func_name, then op_key):
        expected_with_groups = [
            lf_g_f_op1,  # Newest time: 2023-10-26 10:00:01
            lf_g_f_op0,  # 2023-10-26 10:00:00, group, f, op
            lf_ga_fa_op,  # 2023-10-26 10:00:00, group_a, func_a, op
            lf_ga_fa_opa,  # 2023-10-26 10:00:00, group_a, func_a, op_a
            lf_ga_fb_op,  # 2023-10-26 10:00:00, group_a, func_b, op
            lf_gb_fa_op,  # 2023-10-26 10:00:00, group_b, func_a, op
            lf_old_day,  # Oldest time: 2023-10-25 12:00:00
        ]

        assert sorted_with_groups == expected_with_groups


# --- Tests for LogFuncDir ---


class TestLogFuncDir:
    def test_creation_valid(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "test_group", "my_func", tmp_path)
        assert lfd.date_day == "2023-10-26"
        assert lfd.group == "test_group"
        assert lfd.func_name == "my_func"
        assert lfd._base_dir == tmp_path

    def test_creation_invalid_date_day(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in YYYY-MM-DD format"):
            LogFuncDir("2023/10/26", "test_group", "my_func", tmp_path)

    def test_date_obj(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "test_group", "my_func", tmp_path)
        assert lfd._date_obj == datetime.date(2023, 10, 26)

    def test_get_dir_path(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "test_group", "my_func", tmp_path)
        expected = tmp_path / "2023-10-26" / "test_group" / "my_func"
        assert lfd.get_dir_path() == expected

    def test_get_log_files_empty_or_missing(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "test_group", "non_existent_func", tmp_path)
        assert lfd.get_log_files() == []  # Dir does not exist

        dir_path = lfd.get_dir_path()
        dir_path.mkdir(parents=True, exist_ok=True)  # Dir exists but empty
        assert lfd.get_log_files() == []

    def test_get_log_files_populated(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        base = tmp_path
        lfd = LogFuncDir("2023-10-26", "test_group", "my_func", base)
        dir_path = lfd.get_dir_path()
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create some log files
        lf1_path = dir_path / "10-00-01_op1.log"
        lf1_path.touch()
        lf2_path = (
            dir_path / "09-00-00_op2.log"
        )  # Older, but will be sorted newer first
        lf2_path.touch()
        lf3_path = dir_path / "10-00-00_op0.log"  # Same time as lf1, op0 < op1
        lf3_path.touch()

        # Create a non-log file and a malformed log file
        (dir_path / "not_a_log.txt").touch()
        (
            dir_path / "malformed.log"
        ).touch()  # Will cause ValueError in LogFile.from_path

        with caplog.at_level(logging.WARNING):
            log_files = lfd.get_log_files()

        assert len(log_files) == 3
        assert any(
            "Skipping malformed log file 'malformed.log'" in record.message
            for record in caplog.records
        )

        # Expected order: newest first (10-00-01_op1, then 10-00-00_op0, then 09-00-00_op2)
        # Sorting by LogFile: newest datetime first, then group (same here), then func_name (same here), then op_key
        expected_lf1 = LogFile.from_path(lf1_path)
        expected_lf2 = LogFile.from_path(lf2_path)
        expected_lf3 = LogFile.from_path(lf3_path)

        assert log_files[0] == expected_lf1  # 10-00-01_op1
        assert log_files[1] == expected_lf3  # 10-00-00_op0 (op0 < op1)
        assert log_files[2] == expected_lf2  # 09-00-00_op2

    def test_equality(self, tmp_path: Path) -> None:
        lfd1 = LogFuncDir("2023-10-26", "group_a", "func_a", tmp_path)
        lfd2 = LogFuncDir("2023-10-26", "group_a", "func_a", tmp_path)
        lfd3 = LogFuncDir("2023-10-27", "group_a", "func_a", tmp_path)  # Diff date
        lfd4 = LogFuncDir("2023-10-26", "group_a", "func_b", tmp_path)  # Diff func_name
        lfd5 = LogFuncDir("2023-10-26", "group_b", "func_a", tmp_path)  # Diff group
        assert lfd1 == lfd2
        assert lfd1 != lfd3
        assert lfd1 != lfd4
        assert lfd1 != lfd5
        assert lfd1 != "not a logfuncdir"

    def test_ordering(self, tmp_path: Path) -> None:
        # Newest date first
        lfd_new_date = LogFuncDir("2023-10-27", "group_a", "func_a", tmp_path)
        lfd_old_date = LogFuncDir("2023-10-26", "group_a", "func_a", tmp_path)

        # Same date, different group (alphabetical)
        lfd_group_a = LogFuncDir("2023-10-26", "group_a", "func_a", tmp_path)
        lfd_group_b = LogFuncDir("2023-10-26", "group_b", "func_a", tmp_path)

        # Same date, same group, different func_name (alphabetical)
        lfd_func_a = LogFuncDir("2023-10-26", "group_a", "func_a", tmp_path)
        lfd_func_b = LogFuncDir("2023-10-26", "group_a", "func_b", tmp_path)

        assert (
            lfd_new_date < lfd_old_date
        )  # lfd_new_date is "less than" because it's newer
        assert lfd_group_a < lfd_group_b
        assert lfd_func_a < lfd_func_b

        # Expected sort: lfd_new_date, then lfd_func_a, then lfd_func_b, then lfd_old_date (if func_a different)
        # but lfd_old_date and lfd_func_a are same date.
        # Expected: lfd_new_date, then lfd_func_a (same date as old_date but func_a<func_a is false, it's equal so goes by obj id or first seen?)
        # Ok, LogFuncDir same date, sort by func_name. lfd_old_date is func_a.
        # So: lfd_new_date (2023-10-27, func_a)
        #     lfd_func_a (2023-10-26, func_a)
        #     lfd_old_date (2023-10-26, func_a) -- wait, lfd_func_a IS lfd_old_date content-wise if func_name 'func_a'
        #     lfd_func_b (2023-10-26, func_b)

        # Test sorting with groups
        lfd1 = LogFuncDir("2023-10-27", "group_z", "z_func", tmp_path)  # Newest date
        lfd2 = LogFuncDir(
            "2023-10-26", "group_a", "a_func", tmp_path
        )  # Older date, alpha first group and func
        lfd3 = LogFuncDir(
            "2023-10-26", "group_a", "b_func", tmp_path
        )  # Older date, same group, alpha second func
        lfd4 = LogFuncDir(
            "2023-10-26", "group_b", "a_func", tmp_path
        )  # Older date, alpha second group

        items_redefined = [lfd4, lfd3, lfd1, lfd2]
        sorted_items = sorted(items_redefined)
        # Expected order: newest date first, then by group, then by func_name
        expected_sorted = [lfd1, lfd2, lfd3, lfd4]
        assert sorted_items == expected_sorted


# --- Tests for LogDayDir ---


class TestLogDayDir:
    def test_creation_valid(self, tmp_path: Path) -> None:
        ldd = LogDayDir("2023-10-26", tmp_path)
        assert ldd.date_day == "2023-10-26"
        assert ldd._base_dir == tmp_path

    def test_creation_invalid_date_day(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in YYYY-MM-DD format"):
            LogDayDir("2023/10/26", tmp_path)

    def test_date_obj(self, tmp_path: Path) -> None:
        ldd = LogDayDir("2023-10-26", tmp_path)
        assert ldd._date_obj == datetime.date(2023, 10, 26)

    def test_get_dir_path(self, tmp_path: Path) -> None:
        ldd = LogDayDir("2023-10-26", tmp_path)
        expected = tmp_path / "2023-10-26"
        assert ldd.get_dir_path() == expected

    def test_get_log_files_empty_or_missing(
        self, tmp_path: Path
    ) -> None:  # Renamed from get_log_files for clarity here
        ldd = LogDayDir("2023-10-26", tmp_path)
        assert ldd.get_log_files() == []  # Dir does not exist

        dir_path = ldd.get_dir_path()
        dir_path.mkdir(parents=True, exist_ok=True)  # Dir exists but empty
        assert ldd.get_log_files() == []

    def test_get_log_files_populated(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:  # Renamed
        base = tmp_path
        ldd = LogDayDir("2023-10-26", base)
        day_dir_path = ldd.get_dir_path()
        day_dir_path.mkdir(parents=True, exist_ok=True)

        # Create group dirs with func dirs inside
        group_a_path = day_dir_path / "group_a"
        group_a_path.mkdir()
        func_a_path = group_a_path / "func_a"
        func_a_path.mkdir()
        func_b_path = group_a_path / "func_b"
        func_b_path.mkdir()

        group_b_path = day_dir_path / "group_b"
        group_b_path.mkdir()
        func_c_path = group_b_path / "func_c"
        func_c_path.mkdir()

        # Create a non-dir and a malformed func dir name (if your logic would try to parse it)
        (day_dir_path / "not_a_dir.txt").touch()
        # LogDayDir's get_log_files doesn't try to parse func dir names for validity beyond being a dir
        # The warning in LogDayDir.get_log_files is for ValueError from LogFuncDir init
        # which can only happen if self.date_day is bad, but it's validated in LogDayDir.__post_init__.
        # So, the warning there is unlikely to trigger from func_dir_path.name issues.

        with caplog.at_level(logging.WARNING):
            log_group_dirs = ldd.get_log_files()

        assert len(log_group_dirs) == 2  # group_a and group_b
        # No warnings expected from this specific setup for LogDayDir.get_log_files
        # assert not any("Skipping malformed group directory" in record.message for record in caplog.records)

        # Expected order: group alphabetical
        expected_lgd_a = LogGroupDir("2023-10-26", "group_a", base)
        expected_lgd_b = LogGroupDir("2023-10-26", "group_b", base)

        assert log_group_dirs[0] == expected_lgd_a
        assert log_group_dirs[1] == expected_lgd_b

        # Test that each group directory contains the expected function directories
        group_a_funcs = log_group_dirs[0].get_log_files()
        assert len(group_a_funcs) == 2  # func_a and func_b
        assert group_a_funcs[0].func_name == "func_a"
        assert group_a_funcs[1].func_name == "func_b"

        group_b_funcs = log_group_dirs[1].get_log_files()
        assert len(group_b_funcs) == 1  # func_c
        assert group_b_funcs[0].func_name == "func_c"

    def test_equality(self, tmp_path: Path) -> None:
        ldd1 = LogDayDir("2023-10-26", tmp_path)
        ldd2 = LogDayDir("2023-10-26", tmp_path)
        ldd3 = LogDayDir("2023-10-27", tmp_path)  # Diff date
        ldd4 = LogDayDir("2023-10-26", tmp_path / "other_base")  # Diff base
        assert ldd1 == ldd2
        assert ldd1 != ldd3
        assert ldd1 != ldd4
        assert ldd1 != "not a logdaydir"

    def test_ordering(self, tmp_path: Path) -> None:
        ldd_new = LogDayDir("2023-10-27", tmp_path)
        ldd_old = LogDayDir("2023-10-26", tmp_path)
        ldd_ancient = LogDayDir("2023-01-01", tmp_path)

        assert ldd_new < ldd_old  # ldd_new is "less than" because it's newer
        assert ldd_old < ldd_ancient

        items = [ldd_ancient, ldd_new, ldd_old]
        sorted_items = sorted(items)
        expected_sorted = [ldd_new, ldd_old, ldd_ancient]
        assert sorted_items == expected_sorted

    def test_get_log_files_returns_correct_groups(self, tmp_path: Path) -> None:
        """Test that get_log_files returns LogGroupDir objects with correct group names."""
        base = tmp_path
        ldd = LogDayDir("2023-10-26", base)
        day_dir_path = ldd.get_dir_path()
        day_dir_path.mkdir(parents=True, exist_ok=True)

        # Create multiple group directories with different names
        groups_to_create = ["auth", "database", "api", "web_ui"]
        expected_groups = []

        for group_name in groups_to_create:
            group_path = day_dir_path / urllib.parse.quote(group_name, safe="")
            group_path.mkdir()
            # Create at least one function directory to make it valid
            func_path = group_path / "test_func"
            func_path.mkdir()
            expected_groups.append(group_name)

        # Also create a group with special characters that need URL encoding
        special_group = "my group & special!"
        encoded_special_group = urllib.parse.quote(special_group, safe="")
        special_group_path = day_dir_path / encoded_special_group
        special_group_path.mkdir()
        (special_group_path / "test_func").mkdir()
        expected_groups.append(special_group)

        # Get the log group directories
        log_group_dirs = ldd.get_log_files()

        # Verify we get the correct number of groups
        assert len(log_group_dirs) == len(expected_groups)

        # Verify each group has the correct name (should be URL-decoded)
        actual_groups = [lgd.group for lgd in log_group_dirs]

        # Sort both lists for comparison since order might vary
        assert sorted(actual_groups) == sorted(expected_groups)

        # Verify that each LogGroupDir object has the correct properties
        for lgd in log_group_dirs:
            assert lgd.date_day == "2023-10-26"
            assert lgd._base_dir == base
            assert lgd.group in expected_groups
            # Verify the group directory path exists (with URL encoding applied)
            expected_path = day_dir_path / urllib.parse.quote(lgd.group, safe="")
            assert expected_path.exists()
            assert expected_path.is_dir()


# --- Tests for LogManager ---


class TestLogManager:
    def test_create_log_file(
        self, log_manager: LogManager, base_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        op_key = "test_op_123"
        log_file_obj = log_manager.create_log_file(sample_func_one, op_key)

        now = datetime.datetime.now(tz=datetime.UTC)
        expected_date_day = now.strftime("%Y-%m-%d")
        expected_date_second = now.strftime(
            "%H-%M-%S"
        )  # Approximation, could be off by 1 sec

        assert log_file_obj.op_key == op_key
        assert log_file_obj.func_name == sample_func_one.__name__
        assert log_file_obj.date_day == expected_date_day
        # Allow for slight time difference due to execution
        created_dt = (
            datetime.datetime.strptime(log_file_obj.date_second, "%H-%M-%S")
            .replace(tzinfo=datetime.UTC)
            .time()
        )
        expected_dt_approx = (
            datetime.datetime.strptime(expected_date_second, "%H-%M-%S")
            .replace(tzinfo=datetime.UTC)
            .time()
        )
        time_diff = datetime.datetime.combine(
            datetime.date.min, created_dt
        ) - datetime.datetime.combine(datetime.date.min, expected_dt_approx)
        assert abs(time_diff.total_seconds()) <= 1  # Allow 1 second diff

        expected_path = (
            base_dir
            / expected_date_day
            / "default"  # Default group
            / sample_func_one.__name__
            / f"{log_file_obj.date_second}_{op_key}.log"  # Use actual created second
        )
        assert expected_path.exists()
        assert expected_path.is_file()

        # Test creating it again (should fail)
        # Need to mock datetime.now to ensure same filename for collision test
        class MockDateTimeExact(datetime.datetime):
            _val = datetime.datetime.strptime(
                f"{log_file_obj.date_day} {log_file_obj.date_second}",
                "%Y-%m-%d %H-%M-%S",
            ).replace(tzinfo=datetime.UTC)

            @classmethod
            def now(cls: Any, tz: Any = None) -> "MockDateTimeExact":
                return cls._val

        monkeypatch.setattr(datetime, "datetime", MockDateTimeExact)
        with pytest.raises(FileExistsError, match="BUG! Log file .* already exists"):
            log_manager.create_log_file(sample_func_one, op_key)

    def test_list_log_days_empty(self, log_manager: LogManager) -> None:
        assert log_manager.list_log_days() == []
        log_manager.base_dir.mkdir()  # Create base_dir but keep it empty
        assert log_manager.list_log_days() == []

    def test_list_log_days_populated(
        self,
        populated_log_structure: tuple[LogManager, Path, dict[str, LogFile]],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        log_manager, base_dir, _ = populated_log_structure
        with caplog.at_level(logging.WARNING):
            day_dirs: list[LogDayDir] = log_manager.list_log_days()

        assert len(day_dirs) == 2  # 2023-10-27 and 2023-10-26
        assert day_dirs[0].date_day == "2023-10-27"  # Newest first
        assert day_dirs[1].date_day == "2023-10-26"

        # Add a non-dir file to base_dir
        (base_dir / "some_file.txt").touch()
        day_dirs_after_file: list[LogDayDir] = log_manager.list_log_days()
        assert len(day_dirs_after_file) == 2  # Should not affect count

    def test_get_log_file_not_found(
        self, populated_log_structure: tuple[LogManager, Path, dict[str, LogFile]]
    ) -> None:
        log_manager, _, _ = populated_log_structure
        assert log_manager.get_log_file("non_existent_op_key") is None

    def test_get_log_file_found_no_specific_date(
        self, populated_log_structure: tuple[LogManager, Path, dict[str, LogFile]]
    ) -> None:
        log_manager, _, created_files = populated_log_structure
        found_log_file = log_manager.get_log_file("op_key_A1")
        assert found_log_file is not None
        assert found_log_file == created_files["lf1"]

        found_log_file_newest = log_manager.get_log_file("op_key_A3_day2")
        assert found_log_file_newest is not None
        assert found_log_file_newest == created_files["lf4"]

    def test_get_log_file_found_with_specific_date(
        self, populated_log_structure: tuple[LogManager, Path, dict[str, LogFile]]
    ) -> None:
        log_manager, _, created_files = populated_log_structure
        found_log_file = log_manager.get_log_file(
            "op_key_A1", specific_date_day="2023-10-26"
        )
        assert found_log_file is not None
        assert found_log_file == created_files["lf1"]

        assert (
            log_manager.get_log_file("op_key_A1", specific_date_day="2023-10-27")
            is None
        )

    def test_get_log_file_specific_date_not_exists(
        self, populated_log_structure: tuple[LogManager, Path, dict[str, LogFile]]
    ) -> None:
        log_manager, _, _ = populated_log_structure
        assert (
            log_manager.get_log_file("any_op_key", specific_date_day="1999-01-01")
            is None
        )

    def test_get_log_file_specific_date_invalid_format(
        self, populated_log_structure: tuple[LogManager, Path, dict[str, LogFile]]
    ) -> None:
        log_manager, _, _ = populated_log_structure
        assert (
            log_manager.get_log_file("any_op_key", specific_date_day="2023/01/01")
            is None
        )


# --- Tests for URL encoding/decoding of group names ---


class TestGroupURLEncoding:
    def test_group_with_special_characters(self, tmp_path: Path) -> None:
        """Test that group names with special characters are URL encoded/decoded correctly."""

        # Test group name with spaces and special characters
        group_name = "my group with spaces & special chars!"
        encoded_group = urllib.parse.quote(group_name, safe="")

        log_manager = LogManager(base_dir=tmp_path)
        log_file = log_manager.create_log_file(sample_func_one, "test_op", group_name)

        # Check that the group is stored correctly (not encoded in the LogFile object)
        assert log_file.group == group_name

        # Check that the file path uses the encoded version
        file_path = log_file.get_file_path()
        assert encoded_group in str(file_path)
        assert file_path.exists()

        # Test that we can read it back correctly
        read_log_file = LogFile.from_path(file_path)
        assert read_log_file.group == group_name  # Should be decoded back
        assert read_log_file == log_file

    def test_group_with_forward_slash(self, tmp_path: Path) -> None:
        """Test that group names with forward slashes are handled correctly."""

        group_name = "parent/child"
        encoded_group = urllib.parse.quote(group_name, safe="")

        log_manager = LogManager(base_dir=tmp_path)
        log_file = log_manager.create_log_file(sample_func_one, "test_op", group_name)

        file_path = log_file.get_file_path()
        assert encoded_group in str(file_path)
        assert (
            "/" not in file_path.parent.parent.name
        )  # The group directory name should be encoded
        assert file_path.exists()

        # Verify round-trip
        read_log_file = LogFile.from_path(file_path)
        assert read_log_file.group == group_name

    def test_group_unicode_characters(self, tmp_path: Path) -> None:
        """Test that group names with Unicode characters are handled correctly."""

        group_name = "测试组 🚀"
        encoded_group = urllib.parse.quote(group_name, safe="")

        log_manager = LogManager(base_dir=tmp_path)
        log_file = log_manager.create_log_file(sample_func_one, "test_op", group_name)

        file_path = log_file.get_file_path()
        assert encoded_group in str(file_path)
        assert file_path.exists()

        # Verify round-trip
        read_log_file = LogFile.from_path(file_path)
        assert read_log_file.group == group_name


# --- Tests for group directory creation and traversal ---


class TestGroupDirectoryHandling:
    def test_create_log_file_with_custom_group(self, tmp_path: Path) -> None:
        """Test creating log files with custom group names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Create log files with different groups
        lf1 = log_manager.create_log_file(sample_func_one, "op1", "auth")
        lf2 = log_manager.create_log_file(sample_func_two, "op2", "database")
        lf3 = log_manager.create_log_file(sample_func_one, "op3")  # default group

        assert lf1.group == "auth"
        assert lf2.group == "database"
        assert lf3.group == "default"  # Default group

        # Check that the directory structure is correct
        today = lf1.date_day
        assert (tmp_path / today / "auth" / sample_func_one.__name__).exists()
        assert (tmp_path / today / "database" / sample_func_two.__name__).exists()
        assert (tmp_path / today / "default" / sample_func_one.__name__).exists()

    def test_list_log_days_with_groups(self, tmp_path: Path) -> None:
        """Test that LogDayDir correctly traverses group directories."""
        log_manager = LogManager(base_dir=tmp_path)

        # Create log files with different groups
        log_manager.create_log_file(sample_func_one, "op1", "auth")
        log_manager.create_log_file(sample_func_two, "op2", "database")
        log_manager.create_log_file(sample_func_one, "op3", "auth")  # Same group as lf1

        # Get the day directory and check its contents
        day_dirs = log_manager.list_log_days()
        assert len(day_dirs) == 1

        log_group_dirs = day_dirs[0].get_log_files()
        assert len(log_group_dirs) == 2  # auth and database groups

        # Check that we have the correct groups
        groups = [lgd.group for lgd in log_group_dirs]
        expected_groups = ["auth", "database"]
        # Sort both for comparison since order might vary
        assert sorted(groups) == sorted(expected_groups)

        # Check function directories within each group
        all_funcs = []
        for group_dir in log_group_dirs:
            func_dirs = group_dir.get_log_files()
            for func_dir in func_dirs:
                all_funcs.append((func_dir.group, func_dir.func_name))

        expected_funcs = [
            ("auth", sample_func_one.__name__),
            ("database", sample_func_two.__name__),
        ]
        assert sorted(all_funcs) == sorted(expected_funcs)

    def test_get_log_file_across_groups(self, tmp_path: Path) -> None:
        """Test that get_log_file can find files across different groups."""
        log_manager = LogManager(base_dir=tmp_path)

        # Create log files with same op_key but different groups
        lf1 = log_manager.create_log_file(sample_func_one, "shared_op", "auth")
        lf2 = log_manager.create_log_file(sample_func_two, "shared_op", "database")
        lf3 = log_manager.create_log_file(sample_func_one, "unique_op", "auth")

        # get_log_file should find the first match (implementation detail: depends on sort order)
        found_shared = log_manager.get_log_file("shared_op")
        assert found_shared is not None
        assert found_shared.op_key == "shared_op"
        # Could be either lf1 or lf2 depending on sort order
        assert found_shared in [lf1, lf2]

        found_unique = log_manager.get_log_file("unique_op")
        assert found_unique == lf3

        not_found = log_manager.get_log_file("nonexistent_op")
        assert not_found is None
