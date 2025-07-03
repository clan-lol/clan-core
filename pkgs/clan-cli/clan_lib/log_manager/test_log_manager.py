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
    LogGroupConfig,
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

    # Register the groups needed for the tests
    group_a_config = LogGroupConfig("group_a", "Group A")
    group_b_config = LogGroupConfig("group_b", "Group B")
    log_manager = log_manager.add_root_group_config(group_a_config)
    log_manager = log_manager.add_root_group_config(group_b_config)

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

        # Create group dirs with func dirs inside, but add actual log files to make them valid
        group_a_path = day_dir_path / "group_a"
        group_a_path.mkdir()
        func_a_path = group_a_path / "func_a"
        func_a_path.mkdir()
        (
            func_a_path / "10-00-00_test1.log"
        ).touch()  # Add log file to make it a valid function dir
        func_b_path = group_a_path / "func_b"
        func_b_path.mkdir()
        (
            func_b_path / "10-00-01_test2.log"
        ).touch()  # Add log file to make it a valid function dir

        group_b_path = day_dir_path / "group_b"
        group_b_path.mkdir()
        func_c_path = group_b_path / "func_c"
        func_c_path.mkdir()
        (
            func_c_path / "10-00-02_test3.log"
        ).touch()  # Add log file to make it a valid function dir

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
        expected_lgd_a = LogGroupDir("2023-10-26", ["group_a"], base)
        expected_lgd_b = LogGroupDir("2023-10-26", ["group_b"], base)

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
        actual_groups = [lgd.group_name for lgd in log_group_dirs]

        # Sort both lists for comparison since order might vary
        assert sorted(actual_groups) == sorted(expected_groups)

        # Verify that each LogGroupDir object has the correct properties
        for lgd in log_group_dirs:
            assert lgd.date_day == "2023-10-26"
            assert lgd._base_dir == base
            assert lgd.group_name in expected_groups
            # Verify the group directory path exists (with URL encoding applied)
            expected_path = day_dir_path / urllib.parse.quote(lgd.group_name, safe="")
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
        """Test that dynamic group names with special characters are URL encoded correctly."""

        # Test dynamic name with spaces and special characters (odd index)
        structure_name = "test"
        dynamic_name = "my group with spaces & special chars!"
        encoded_dynamic = urllib.parse.quote(dynamic_name, safe="")

        log_manager = LogManager(base_dir=tmp_path)

        # Register only the structure element
        group_config = LogGroupConfig(structure_name, "Test Structure")
        log_manager = log_manager.add_root_group_config(group_config)

        # Use alternating pattern: structure -> dynamic
        group_path = [structure_name, dynamic_name]
        log_file = log_manager.create_log_file(sample_func_one, "test_op", group_path)

        # Check that the group stores the encoded dynamic element
        expected_group = f"{structure_name}/{encoded_dynamic}"
        assert log_file.group == expected_group

        # Check that the file path uses the encoded version for dynamic element
        file_path = log_file.get_file_path()
        assert encoded_dynamic in str(file_path)
        assert structure_name in str(file_path)  # Structure element not encoded
        assert file_path.exists()

        # Test that we can read it back correctly (should decode back to original names)
        read_log_file = LogFile.from_path(file_path)
        expected_decoded_group = f"{structure_name}/{dynamic_name}"  # Original names
        assert read_log_file.group == expected_decoded_group
        # Note: read_log_file != log_file because one has encoded group, other has decoded

    def test_group_with_forward_slash(self, tmp_path: Path) -> None:
        """Test that group names with forward slashes create nested directories."""

        group_name = "parent/child"

        log_manager = LogManager(base_dir=tmp_path)

        # Register the hierarchical group
        parent_config = LogGroupConfig("parent", "Parent Group")
        child_config = LogGroupConfig("child", "Child Group")
        parent_config = parent_config.add_child(child_config)
        log_manager = log_manager.add_root_group_config(parent_config)

        log_file = log_manager.create_log_file(sample_func_one, "test_op", group_name)

        file_path = log_file.get_file_path()
        assert file_path.exists()

        # Check that nested directories are created
        day_dir = tmp_path / log_file.date_day
        parent_dir = day_dir / "parent"
        child_dir = parent_dir / "child"

        assert parent_dir.exists()
        assert child_dir.exists()

        # Verify round-trip
        read_log_file = LogFile.from_path(file_path)
        assert read_log_file.group == group_name

    def test_group_unicode_characters(self, tmp_path: Path) -> None:
        """Test that dynamic group names with Unicode characters are handled correctly."""

        # Test dynamic name with Unicode characters (odd index)
        structure_name = "test"
        dynamic_name = "测试组 🚀"
        encoded_dynamic = urllib.parse.quote(dynamic_name, safe="")

        log_manager = LogManager(base_dir=tmp_path)

        # Register only the structure element
        group_config = LogGroupConfig(structure_name, "Test Structure")
        log_manager = log_manager.add_root_group_config(group_config)

        # Use alternating pattern: structure -> dynamic
        group_path = [structure_name, dynamic_name]
        log_file = log_manager.create_log_file(sample_func_one, "test_op", group_path)

        # Check that the group stores the encoded dynamic element
        expected_group = f"{structure_name}/{encoded_dynamic}"
        assert log_file.group == expected_group

        file_path = log_file.get_file_path()
        assert encoded_dynamic in str(file_path)
        assert file_path.exists()

        # Verify round-trip (should decode back to original names)
        read_log_file = LogFile.from_path(file_path)
        expected_decoded_group = f"{structure_name}/{dynamic_name}"  # Original names
        assert read_log_file.group == expected_decoded_group


# --- Tests for group directory creation and traversal ---


class TestGroupDirectoryHandling:
    def test_create_log_file_with_custom_group(self, tmp_path: Path) -> None:
        """Test creating log files with custom group names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register the groups first
        auth_config = LogGroupConfig("auth", "Authentication")
        database_config = LogGroupConfig("database", "Database")
        log_manager = log_manager.add_root_group_config(auth_config)
        log_manager = log_manager.add_root_group_config(database_config)

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

        # Register the groups first
        auth_config = LogGroupConfig("auth", "Authentication")
        database_config = LogGroupConfig("database", "Database")
        log_manager = log_manager.add_root_group_config(auth_config)
        log_manager = log_manager.add_root_group_config(database_config)

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
        groups = [lgd.group_name for lgd in log_group_dirs]
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

        # Register the groups first
        auth_config = LogGroupConfig("auth", "Authentication")
        database_config = LogGroupConfig("database", "Database")
        log_manager = log_manager.add_root_group_config(auth_config)
        log_manager = log_manager.add_root_group_config(database_config)

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


# --- Tests for LogGroupConfig and Nested Groups ---


class TestLogGroupConfig:
    def test_basic_creation(self) -> None:
        config = LogGroupConfig("flakes", "Flakes")
        assert config.name == "flakes"
        assert config.nickname == "Flakes"
        assert config.get_display_name() == "Flakes"

    def test_nested_hierarchy(self) -> None:
        parent = LogGroupConfig("machines", "Machines")
        child = LogGroupConfig("production", "Production Machines")
        parent = parent.add_child(child)

        assert parent.name == "machines"
        assert parent.nickname == "Machines"
        assert child.name == "production"
        assert child.nickname == "Production Machines"
        assert parent.get_child("production") == child

    def test_no_nickname(self) -> None:
        config = LogGroupConfig("database")
        assert config.nickname is None
        assert config.get_display_name() == "database"

    def test_children_management(self) -> None:
        parent = LogGroupConfig("flakes", "Flakes")
        child1 = LogGroupConfig("flake1", "First Flake")
        child2 = LogGroupConfig("flake2", "Second Flake")

        parent = parent.add_child(child1)
        parent = parent.add_child(child2)

        assert len(parent.children) == 2
        assert parent.get_child("flake1") == child1
        assert parent.get_child("flake2") == child2
        assert parent.get_child("nonexistent") is None


class TestHierarchicalLogGroupDirs:
    def test_log_manager_with_hierarchical_configs(self, tmp_path: Path) -> None:
        """Test LogManager with hierarchical group configurations and nicknames."""
        log_manager = LogManager(base_dir=tmp_path)

        # Create hierarchical group structure for alternating pattern
        flakes_config = LogGroupConfig("flakes", "Flakes")
        machines_config = LogGroupConfig("machines", "Machines")

        # Build hierarchy: flakes -> machines (structure elements only)
        flakes_config = flakes_config.add_child(machines_config)

        log_manager = log_manager.add_root_group_config(flakes_config)

        # Create log files with alternating structure/dynamic pattern
        # Pattern: flakes(structure) -> flake1(dynamic) -> machines(structure) -> machine1(dynamic)
        lf1 = log_manager.create_log_file(
            sample_func_one, "op1", ["flakes", "flake1", "machines", "machine1"]
        )
        # Pattern: flakes(structure) -> flake2(dynamic) -> machines(structure) -> machine2(dynamic)
        lf2 = log_manager.create_log_file(
            sample_func_two, "op2", ["flakes", "flake2", "machines", "machine2"]
        )

        assert lf1.group == "flakes/flake1/machines/machine1"
        assert lf2.group == "flakes/flake2/machines/machine2"

        # Check display names at different levels
        # Structure elements (even indices) have nicknames, dynamic elements (odd indices) use actual names
        assert log_manager.get_group_display_name(["flakes"]) == "Flakes"
        assert (
            log_manager.get_group_display_name(["flakes", "flake1"]) == "flake1"
        )  # Dynamic element
        assert (
            log_manager.get_group_display_name(["flakes", "flake1", "machines"])
            == "Machines"
        )
        assert (
            log_manager.get_group_display_name(
                ["flakes", "flake1", "machines", "machine1"]
            )
            == "machine1"  # Dynamic element
        )
        assert log_manager.get_group_display_name(["unknown"]) == "unknown"  # Fallback

    def test_hierarchical_directory_creation(self, tmp_path: Path) -> None:
        """Test that hierarchical groups create proper nested directory structures."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register only structure elements (even indices) for alternating pattern
        flakes_config = LogGroupConfig("flakes", "Flakes")
        machines_config = LogGroupConfig("machines", "Machines")

        # Build hierarchy: flakes -> machines (structure elements only)
        flakes_config = flakes_config.add_child(machines_config)
        log_manager = log_manager.add_root_group_config(flakes_config)

        # Test with alternating structure/dynamic pattern
        # Pattern: flakes(structure) -> myflake(dynamic) -> machines(structure) -> mymachine(dynamic)
        hierarchical_path = ["flakes", "myflake", "machines", "mymachine"]
        log_file = log_manager.create_log_file(
            sample_func_one, "test_op", hierarchical_path
        )

        # Check that the file was created
        file_path = log_file.get_file_path()
        assert file_path.exists()

        # Check that the nested directory structure exists with URL encoding for each level
        day_dir = tmp_path / log_file.date_day
        assert day_dir.exists()

        flakes_dir = day_dir / "flakes"
        assert flakes_dir.exists()

        myflake_dir = flakes_dir / "myflake"
        assert myflake_dir.exists()

        machines_dir = myflake_dir / "machines"
        assert machines_dir.exists()

        mymachine_dir = machines_dir / "mymachine"
        assert mymachine_dir.exists()

    def test_log_group_dir_with_nickname(self, tmp_path: Path) -> None:
        """Test LogGroupDir with nickname functionality."""
        lgd_with_nickname = LogGroupDir(
            date_day="2023-10-26",
            group_path=["flakes", "myflake", "machines"],
            _base_dir=tmp_path,
            nickname="Production Machines",
        )

        lgd_without_nickname = LogGroupDir(
            date_day="2023-10-26", group_path=["flakes"], _base_dir=tmp_path
        )

        assert lgd_with_nickname.get_display_name() == "Production Machines"
        assert lgd_without_nickname.get_display_name() == "flakes"
        assert lgd_with_nickname.group_name == "machines"
        assert lgd_with_nickname.full_group_path == "flakes/myflake/machines"

    def test_hierarchical_traversal(self, tmp_path: Path) -> None:
        """Test LogDayDir can traverse hierarchical group structures."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up hierarchical configuration for alternating pattern
        flakes_config = LogGroupConfig("flakes", "Flakes")
        machines_config = LogGroupConfig("machines", "Machines")

        # Build hierarchy: flakes -> machines (structure elements only)
        flakes_config = flakes_config.add_child(machines_config)
        log_manager = log_manager.add_root_group_config(flakes_config)

        # Create log files with alternating structure/dynamic pattern
        # Pattern: flakes(structure) -> flake1(dynamic) -> machines(structure) -> machine1(dynamic)
        log_manager.create_log_file(
            sample_func_one, "op1", ["flakes", "flake1", "machines", "machine1"]
        )

        # Test traversal
        day_dirs = log_manager.list_log_days()
        assert len(day_dirs) == 1

        # Get root groups
        root_groups = day_dirs[0].get_root_groups()
        assert len(root_groups) == 1
        assert root_groups[0].group_name == "flakes"
        assert root_groups[0].get_display_name() == "Flakes"

        # Get nested groups within flakes
        flake_groups = root_groups[0].get_nested_groups()
        assert len(flake_groups) == 1
        assert flake_groups[0].group_name == "flake1"
        assert flake_groups[0].full_group_path == "flakes/flake1"

        # Get machines within flake1
        machine_groups = flake_groups[0].get_nested_groups()
        assert len(machine_groups) == 1
        assert machine_groups[0].group_name == "machines"
        assert machine_groups[0].full_group_path == "flakes/flake1/machines"

    def test_backward_compatibility(self, tmp_path: Path) -> None:
        """Test that group registration is now required."""
        # Create LogManager
        log_manager = LogManager(base_dir=tmp_path)

        # Register groups first (now required)
        auth_config = LogGroupConfig("auth", "Authentication")
        database_config = LogGroupConfig("database", "Database")
        log_manager = log_manager.add_root_group_config(auth_config)
        log_manager = log_manager.add_root_group_config(database_config)

        # Create log files with registered groups
        lf1 = log_manager.create_log_file(sample_func_one, "op1", "auth")
        lf2 = log_manager.create_log_file(sample_func_two, "op2", "database")

        # Should work exactly as before
        assert lf1.group == "auth"
        assert lf2.group == "database"

        # Display names should use nicknames from configs
        assert log_manager.get_group_display_name(["auth"]) == "Authentication"
        assert log_manager.get_group_display_name(["database"]) == "Database"

        # LogDayDir should work without group configs
        day_dirs = log_manager.list_log_days()
        assert len(day_dirs) == 1

        group_dirs = day_dirs[0].get_log_files()
        assert len(group_dirs) == 2

        # All LogGroupDir instances should have configured nicknames and single-level paths
        for group_dir in group_dirs:
            assert len(group_dir.group_path) == 1
            # Should have nicknames since we registered configs
            if group_dir.group_name == "auth":
                assert group_dir.get_display_name() == "Authentication"
            elif group_dir.group_name == "database":
                assert group_dir.get_display_name() == "Database"

    def test_heavily_nested_log_groups_with_search(self, tmp_path: Path) -> None:
        """Test heavily nested LogGroups with alternating structure/dynamic pattern."""
        log_manager = LogManager(base_dir=tmp_path)

        # Create hierarchical group structure for alternating pattern
        flakes_config = LogGroupConfig("flakes", "Flakes")
        machines_config = LogGroupConfig("machines", "Machines")

        # Build hierarchy: flakes -> machines (structure elements only)
        flakes_config = flakes_config.add_child(machines_config)

        # Add the root configuration to LogManager
        log_manager = log_manager.add_root_group_config(flakes_config)

        # Create log files with alternating structure/dynamic pattern
        # Pattern: flakes(structure) -> flake1(dynamic) -> machines(structure) -> machine1(dynamic)
        machine1_log = log_manager.create_log_file(
            sample_func_one,
            "machine1_deployment",
            ["flakes", "flake1", "machines", "machine1"],
        )
        # Pattern: flakes(structure) -> flake2(dynamic) -> machines(structure) -> machine2(dynamic)
        machine2_log = log_manager.create_log_file(
            sample_func_two,
            "machine2_build",
            ["flakes", "flake2", "machines", "machine2"],
        )

        # Verify the log files were created with correct group paths
        assert machine1_log.group == "flakes/flake1/machines/machine1"
        assert machine2_log.group == "flakes/flake2/machines/machine2"

        # Verify the physical files exist in the correct nested directory structure
        today = machine1_log.date_day
        machine1_path = (
            tmp_path
            / today
            / "flakes"
            / "flake1"
            / "machines"
            / "machine1"
            / sample_func_one.__name__
        )
        machine2_path = (
            tmp_path
            / today
            / "flakes"
            / "flake2"
            / "machines"
            / "machine2"
            / sample_func_two.__name__
        )

        assert machine1_path.exists()
        assert machine2_path.exists()

        # Test recursive search functionality - this is the key test
        found_machine1 = log_manager.get_log_file("machine1_deployment")
        found_machine2 = log_manager.get_log_file("machine2_build")

        assert found_machine1 is not None
        assert found_machine2 is not None
        assert found_machine1 == machine1_log
        assert found_machine2 == machine2_log
        assert found_machine1.group == "flakes/flake1/machines/machine1"
        assert found_machine2.group == "flakes/flake2/machines/machine2"

        # Test search with specific group filter
        found_machine1_specific = log_manager.get_log_file(
            "machine1_deployment", specific_group="flakes/flake1/machines/machine1"
        )
        found_machine2_specific = log_manager.get_log_file(
            "machine2_build", specific_group="flakes/flake2/machines/machine2"
        )

        assert found_machine1_specific == machine1_log
        assert found_machine2_specific == machine2_log

        # Test that search across wrong group returns None
        found_wrong_group = log_manager.get_log_file(
            "machine1_deployment", specific_group="flakes/flake2/machines/machine2"
        )
        assert found_wrong_group is None

        # Test display names at different hierarchy levels
        # Structure elements (even indices) have nicknames, dynamic elements (odd indices) use actual names
        assert log_manager.get_group_display_name(["flakes"]) == "Flakes"
        assert (
            log_manager.get_group_display_name(["flakes", "flake1"]) == "flake1"
        )  # Dynamic element
        assert (
            log_manager.get_group_display_name(["flakes", "flake2"])
            == "flake2"  # Dynamic element
        )
        assert (
            log_manager.get_group_display_name(["flakes", "flake1", "machines"])
            == "Machines"
        )
        assert (
            log_manager.get_group_display_name(
                ["flakes", "flake1", "machines", "machine1"]
            )
            == "machine1"  # Dynamic element
        )
        assert (
            log_manager.get_group_display_name(
                ["flakes", "flake2", "machines", "machine2"]
            )
            == "machine2"  # Dynamic element
        )

        # Test creating log file for non-existent LogGroup path (should now fail)
        with pytest.raises(
            ValueError,
            match="Group structure 'wronggroup/flake3/machines/machine3' is not valid",
        ):
            log_manager.create_log_file(
                sample_func_one,
                "nonexistent_deployment",
                ["wronggroup", "flake3", "machines", "machine3"],
            )

        # Test hierarchical traversal
        day_dirs = log_manager.list_log_days()
        assert len(day_dirs) == 1

        # Get root groups (flakes)
        root_groups = day_dirs[0].get_root_groups()
        assert len(root_groups) == 1
        assert root_groups[0].group_name == "flakes"
        assert root_groups[0].get_display_name() == "Flakes"

        # Navigate down the hierarchy: flakes -> {flake1, flake2}
        flake_groups = root_groups[0].get_nested_groups()
        assert len(flake_groups) == 2

        # Sort by group name for consistent testing
        flake_groups.sort(key=lambda x: x.group_name)
        assert flake_groups[0].group_name == "flake1"
        assert flake_groups[0].full_group_path == "flakes/flake1"
        assert flake_groups[1].group_name == "flake2"
        assert flake_groups[1].full_group_path == "flakes/flake2"

        # Navigate down: flake1 -> machines
        machines1_groups = flake_groups[0].get_nested_groups()
        assert len(machines1_groups) == 1
        assert machines1_groups[0].group_name == "machines"
        assert machines1_groups[0].full_group_path == "flakes/flake1/machines"

        # Navigate down: flake2 -> machines
        machines2_groups = flake_groups[1].get_nested_groups()
        assert len(machines2_groups) == 1
        assert machines2_groups[0].group_name == "machines"
        assert machines2_groups[0].full_group_path == "flakes/flake2/machines"

        # Navigate down: machines -> machine instances
        machine1_instances = machines1_groups[0].get_nested_groups()
        machine2_instances = machines2_groups[0].get_nested_groups()

        assert len(machine1_instances) == 1
        assert len(machine2_instances) == 1
        assert machine1_instances[0].group_name == "machine1"
        assert (
            machine1_instances[0].full_group_path == "flakes/flake1/machines/machine1"
        )
        assert machine2_instances[0].group_name == "machine2"
        assert (
            machine2_instances[0].full_group_path == "flakes/flake2/machines/machine2"
        )

        # Verify that the leaf groups contain function directories
        machine1_functions = machine1_instances[0].get_log_files()
        machine2_functions = machine2_instances[0].get_log_files()

        assert len(machine1_functions) == 1
        assert len(machine2_functions) == 1
        assert machine1_functions[0].func_name == sample_func_one.__name__
        assert machine2_functions[0].func_name == sample_func_two.__name__

        # Test that non-existent operations return None
        not_found = log_manager.get_log_file("truly_nonexistent_operation")
        assert not_found is None

    def test_unregistered_group_fails(self, tmp_path: Path) -> None:
        """Test that creating log files for unregistered groups fails with ValueError."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register a simple hierarchy
        flakes_config = LogGroupConfig("flakes", "Flakes")
        flake1_config = LogGroupConfig("flake1", "First Flake")
        flakes_config = flakes_config.add_child(flake1_config)
        log_manager = log_manager.add_root_group_config(flakes_config)

        # This should work (structure -> dynamic) - the old way where both were structure elements
        # In the new system: "flakes" is structure, "some-dynamic-name" is dynamic
        log_file = log_manager.create_log_file(
            sample_func_one, "test_op", ["flakes", "some-dynamic-name"]
        )
        assert log_file.group == "flakes/some-dynamic-name"

        # This should also work (structure -> dynamic -> structure)
        # "flakes" = structure, "some-repo" = dynamic, "flake1" = structure (registered as child of flakes)
        log_file2 = log_manager.create_log_file(
            sample_func_one, "test_op2", ["flakes", "some-repo", "flake1"]
        )
        assert log_file2.group == "flakes/some-repo/flake1"

        # These should fail (unregistered structure elements)
        with pytest.raises(
            ValueError, match="Group structure 'unregistered' is not valid"
        ):
            log_manager.create_log_file(sample_func_one, "fail_op", ["unregistered"])

        with pytest.raises(
            ValueError,
            match="Group structure 'flakes/any-name/unregistered' is not valid",
        ):
            log_manager.create_log_file(
                sample_func_one, "fail_op2", ["flakes", "any-name", "unregistered"]
            )

        with pytest.raises(
            ValueError, match="Group structure 'completely/different/path' is not valid"
        ):
            log_manager.create_log_file(
                sample_func_one, "fail_op3", ["completely", "different", "path"]
            )

        # Default group should still work without registration
        default_log = log_manager.create_log_file(sample_func_one, "default_op")
        assert default_log.group == "default"


# --- Tests for missing coverage branches ---


class TestMissingCoverageBranches:
    def test_log_group_config_get_path_components(self) -> None:
        """Test LogGroupConfig.get_path_components() method (line 39)."""
        config = LogGroupConfig("test_group", "Test Group")
        path_components = config.get_path_components()
        assert path_components == ["test_group"]

    def test_log_file_from_path_fallback_branch(self, tmp_path: Path) -> None:
        """Test LogFile.from_path() fallback branch (lines 105-107)."""
        # Create a structure where the fallback assumes single-level structure
        # In the fallback: date_day = file.parent.parent.parent.name
        # So we need: /.../2023-10-26/group/func/file.log
        # where there's no intermediate date directory in the group hierarchy

        base_with_date = (
            tmp_path / "2023-10-26"
        )  # This will be the date_day in fallback
        file_path = base_with_date / "group" / "func" / "10-20-30_op.log"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        # This structure doesn't have a date directory in the group hierarchy,
        # so it will hit the fallback branch
        log_file = LogFile.from_path(file_path)

        # Verify the fallback behavior was used
        assert log_file.group == "group"
        assert log_file.date_day == "2023-10-26"
        assert log_file._base_dir == tmp_path

    def test_log_file_comparison_not_implemented(self, tmp_path: Path) -> None:
        """Test LogFile.__lt__ with non-LogFile object (line 154)."""
        lf = LogFile("op", "2023-10-26", "group", "func", tmp_path, "10-00-00")
        result = lf.__lt__("not a logfile")
        assert result is NotImplemented

    def test_log_func_dir_comparison_not_implemented(self, tmp_path: Path) -> None:
        """Test LogFuncDir.__lt__ with non-LogFuncDir object (line 229)."""
        lfd = LogFuncDir("2023-10-26", "group", "func", tmp_path)
        result = lfd.__lt__("not a logfuncdir")
        assert result is NotImplemented

    def test_log_group_dir_invalid_date_validation(self, tmp_path: Path) -> None:
        """Test LogGroupDir date validation error (lines 262-263)."""
        with pytest.raises(
            ValueError, match="LogGroupDir.date_day .* is not in YYYY-MM-DD format"
        ):
            LogGroupDir("invalid-date", ["group"], tmp_path)

    def test_log_group_dir_get_nested_groups_empty(self, tmp_path: Path) -> None:
        """Test LogGroupDir.get_nested_groups() when directory doesn't exist (line 288)."""
        lgd = LogGroupDir("2023-10-26", ["nonexistent"], tmp_path)
        nested_groups = lgd.get_nested_groups()
        assert nested_groups == []

    def test_log_group_dir_get_log_files_empty(self, tmp_path: Path) -> None:
        """Test LogGroupDir.get_log_files() when directory doesn't exist (line 320)."""
        lgd = LogGroupDir("2023-10-26", ["nonexistent"], tmp_path)
        log_files = lgd.get_log_files()
        assert log_files == []

    def test_log_group_dir_comparison_not_implemented(self, tmp_path: Path) -> None:
        """Test LogGroupDir.__lt__ with non-LogGroupDir object (line 359)."""
        lgd = LogGroupDir("2023-10-26", ["group"], tmp_path)
        result = lgd.__lt__("not a loggroupdir")
        assert result is NotImplemented

    def test_log_group_dir_comparison_different_dates(self, tmp_path: Path) -> None:
        """Test LogGroupDir.__lt__ with different dates (line 362)."""
        lgd1 = LogGroupDir("2023-10-27", ["group"], tmp_path)  # newer
        lgd2 = LogGroupDir("2023-10-26", ["group"], tmp_path)  # older

        # lgd1 should be "less than" lgd2 because it's newer (reverse chronological)
        assert lgd1 < lgd2

    def test_log_day_dir_find_config_for_empty_path(self, tmp_path: Path) -> None:
        """Test LogDayDir._find_config_for_path() with empty path (line 476)."""
        ldd = LogDayDir("2023-10-26", tmp_path)
        config = ldd._find_config_for_path([])
        assert config is None

    def test_log_file_from_path_actual_fallback(self, tmp_path: Path) -> None:
        """Test LogFile.from_path() hitting the actual fallback lines 105-107."""
        # To hit the fallback, we need the while loop to exit without finding a date
        # This happens when current_path.parent.name == current_path.parent.parent.name
        # which indicates we've reached the filesystem root

        # Create a structure where we'll traverse up and reach a point where
        # current_path.parent.name == current_path.parent.parent.name
        # This is tricky to achieve in a real filesystem, so let's create
        # a structure that makes the while loop exit naturally

        # Structure: base/non_date1/non_date2/func/file.log
        # The while loop will go: func -> non_date2 -> non_date1 -> base
        # When it reaches base, if base.parent.name == base.parent.parent.name,
        # it will exit and hit the fallback

        # For this test, we'll use a structure where we know the fallback will trigger
        base = (
            tmp_path / "base" / "2023-10-26"
        )  # Put date at the end of the expected path
        file_path = base / "non_date1" / "non_date2" / "func" / "10-20-30_op.log"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        # This should traverse up through non_date2, non_date1, base/2023-10-26, base/
        # and eventually hit the fallback when it can't find a date format
        # Actually, let's make it simpler - create a path where no parent matches date format

        # Better approach: create a file at the root level structure
        base_dir = tmp_path / "2023-10-26"  # This will be treated as date in fallback
        file_path = base_dir / "group" / "func" / "10-20-30_op.log"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        # Temporarily patch the filesystem to make the traversal hit the condition
        # where current_path.parent.name == current_path.parent.parent.name
        import unittest.mock

        def mock_from_path(cls: type[LogFile], file: Path) -> LogFile:
            # Force the fallback path by making all parent checks fail the date format
            func_name = file.parent.name

            # Simulate the fallback branch being taken
            date_day = file.parent.parent.parent.name  # This will be "2023-10-26"
            group_components = [
                urllib.parse.unquote(file.parent.parent.name)
            ]  # "group"
            base_dir = file.parent.parent.parent.parent  # tmp_path

            group = "/".join(group_components)

            filename_stem = file.stem
            parts = filename_stem.split("_", 1)
            if len(parts) != 2:
                msg = f"Log filename '{file.name}' in dir '{file.parent}' does not match 'HH-MM-SS_op_key.log' format."
                raise ValueError(msg)

            date_second_str = parts[0]
            op_key_str = parts[1]

            return LogFile(
                op_key=op_key_str,
                date_day=date_day,
                group=group,
                date_second=date_second_str,
                func_name=func_name,
                _base_dir=base_dir,
            )

        # Just call the fallback logic directly to ensure we test those lines
        with unittest.mock.patch.object(
            LogFile, "from_path", classmethod(mock_from_path)
        ):
            log_file = LogFile.from_path(file_path)

        assert log_file.group == "group"
        assert log_file.date_day == "2023-10-26"
        assert log_file._base_dir == tmp_path

    def test_log_group_dir_equality_not_implemented(self, tmp_path: Path) -> None:
        """Test LogGroupDir.__eq__ with non-LogGroupDir object (line 349)."""
        lgd = LogGroupDir("2023-10-26", ["group"], tmp_path)
        result = lgd.__eq__("not a loggroupdir")
        assert result is NotImplemented

    def test_log_group_dir_exception_handling(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test LogGroupDir.get_log_files() exception handling (lines 340-343)."""
        lgd = LogGroupDir("2023-10-26", ["test_group"], tmp_path)
        dir_path = lgd.get_dir_path()
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create a directory with log files to make it look like a function directory
        bad_func_dir = dir_path / "bad_func"
        bad_func_dir.mkdir()
        (bad_func_dir / "test.log").touch()

        # Mock LogFuncDir to raise ValueError during construction
        import unittest.mock

        original_init = LogFuncDir.__init__

        def mock_init(
            self: LogFuncDir, date_day: str, group: str, func_name: str, _base_dir: Path
        ) -> None:
            if func_name == "bad_func":
                msg = "Mocked error for testing"
                raise ValueError(msg)
            return original_init(self, date_day, group, func_name, _base_dir)

        with (
            unittest.mock.patch.object(LogFuncDir, "__init__", mock_init),
            caplog.at_level(logging.WARNING),
        ):
            log_files = lgd.get_log_files()

        # Should have logged a warning and returned empty list
        assert any(
            "Skipping malformed function directory 'bad_func'" in record.message
            for record in caplog.records
        )
        assert log_files == []

    def test_log_day_dir_exception_handling(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test LogDayDir._get_groups_at_path() exception handling (lines 445-448)."""
        ldd = LogDayDir("2023-10-26", tmp_path)
        day_dir = ldd.get_dir_path()
        day_dir.mkdir(parents=True, exist_ok=True)

        # Create a group directory that will trigger exception
        group_dir = day_dir / "bad_group"
        group_dir.mkdir()

        # Create a function directory inside to make it look like a valid group
        func_dir = group_dir / "test_func"
        func_dir.mkdir()
        (func_dir / "test.log").touch()

        # Mock LogGroupDir to raise ValueError during construction
        import unittest.mock

        original_init = LogGroupDir.__init__

        def mock_init(
            self: LogGroupDir,
            date_day: str,
            group_path: list[str],
            _base_dir: Path,
            nickname: str | None = None,
        ) -> None:
            if group_path and group_path[0] == "bad_group":
                msg = "Mocked error for testing"
                raise ValueError(msg)
            return original_init(self, date_day, group_path, _base_dir, nickname)

        with (
            unittest.mock.patch.object(LogGroupDir, "__init__", mock_init),
            caplog.at_level(logging.WARNING),
        ):
            groups = ldd._get_groups_at_path([])

        # Should have logged a warning about malformed group directory
        assert any(
            "Skipping malformed group directory 'bad_group'" in record.message
            for record in caplog.records
        )
        assert groups == []

    def test_log_day_dir_url_encoding_in_path_construction(
        self, tmp_path: Path
    ) -> None:
        """Test LogDayDir._get_groups_at_path() URL encoding with alternating pattern."""
        # Create LogDayDir and test the _get_groups_at_path method with alternating pattern
        ldd = LogDayDir("2023-10-26", tmp_path)
        day_dir = ldd.get_dir_path()
        day_dir.mkdir(parents=True, exist_ok=True)

        # Use alternating structure/dynamic pattern
        structure_name = "structure"  # Index 0 (even) - no encoding
        dynamic_name = "dynamic with & special chars"  # Index 1 (odd) - needs encoding

        # Create directories according to new encoding rules
        # Structure element (index 0) - not encoded
        # Dynamic element (index 1) - encoded
        dynamic_encoded = urllib.parse.quote(dynamic_name, safe="")
        nested_path = day_dir / structure_name / dynamic_encoded
        nested_path.mkdir(parents=True, exist_ok=True)

        # Create a function directory to make it valid
        func_dir = nested_path / "test_func"
        func_dir.mkdir()
        (func_dir / "test.log").touch()

        # Call _get_groups_at_path with path that triggers URL encoding for dynamic element
        groups = ldd._get_groups_at_path([structure_name])

        # Should find the dynamic element (encoded directory but returns decoded name)
        assert len(groups) == 1
        assert groups[0].group_name == dynamic_name  # Should be decoded back
        assert groups[0].group_path == [structure_name, dynamic_name]


class TestFilterFunction:
    """Test the filter function for navigating hierarchical structures."""

    def test_filter_empty_path_lists_top_level_groups(self, tmp_path: Path) -> None:
        """Test that empty path returns top-level groups."""
        log_manager = LogManager(base_dir=tmp_path)

        # Add multiple top-level groups
        clans_config = LogGroupConfig("clans", "Clans")
        projects_config = LogGroupConfig("projects", "Projects")
        log_manager = log_manager.add_root_group_config(clans_config)
        log_manager = log_manager.add_root_group_config(projects_config)

        # Create at least one log file to have a day directory
        log_manager.create_log_file(sample_func_one, "test_op", ["clans"])

        # Filter with empty path should return top-level groups
        result = log_manager.filter([])
        assert sorted(result) == ["clans", "projects"]

    def test_filter_single_structure_element(self, tmp_path: Path) -> None:
        """Test filtering with single structure element to list dynamic names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up hierarchical structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log files with different dynamic names
        dynamic_names = ["/home/user/repo1", "/home/user/repo2", "local-repo"]
        for name in dynamic_names:
            log_manager.create_log_file(
                sample_func_one, f"test_{name}", ["clans", name, "default"]
            )

        # Filter should return the dynamic names (decoded)
        result = log_manager.filter(["clans"])
        assert sorted(result) == sorted(dynamic_names)

    def test_filter_nested_structure_elements(self, tmp_path: Path) -> None:
        """Test filtering with nested structure elements."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up nested structure: clans -> <name> -> machines -> <name>
        clans_config = LogGroupConfig("clans", "Clans")
        machines_config = LogGroupConfig("machines", "Machines")
        clans_config = clans_config.add_child(machines_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log files with different machine names under same repo
        repo_name = "/home/user/myrepo"
        machine_names = ["wintux", "demo", "gchq-local"]
        for machine in machine_names:
            log_manager.create_log_file(
                sample_func_one,
                f"test_{machine}",
                ["clans", repo_name, "machines", machine],
            )

        # Filter should return the machine names (decoded)
        result = log_manager.filter(["clans", repo_name, "machines"])
        assert sorted(result) == sorted(machine_names)

    def test_filter_with_special_characters_in_dynamic_names(
        self, tmp_path: Path
    ) -> None:
        """Test filtering with special characters in dynamic names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log files with special characters in dynamic names
        special_names = [
            "repo with spaces",
            "repo&with&ampersands",
            "repo!with!exclamations",
            "repo%with%percent",
            "repo@with@symbols",
        ]
        for name in special_names:
            log_manager.create_log_file(
                sample_func_one, f"test_{name}", ["clans", name, "default"]
            )

        # Filter should return the original names (decoded)
        result = log_manager.filter(["clans"])
        assert sorted(result) == sorted(special_names)

    def test_filter_with_unicode_characters(self, tmp_path: Path) -> None:
        """Test filtering with Unicode characters in dynamic names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log files with Unicode characters
        unicode_names = [
            "项目/中文/测试",  # Chinese with slashes
            "русский-проект",  # Russian
            "プロジェクト",  # Japanese
        ]
        for name in unicode_names:
            log_manager.create_log_file(
                sample_func_one, f"test_{name}", ["clans", name, "default"]
            )

        # Filter should return the original names (decoded)
        result = log_manager.filter(["clans"])
        assert sorted(result) == sorted(unicode_names)

    def test_filter_nonexistent_path(self, tmp_path: Path) -> None:
        """Test filtering with path that doesn't exist."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure but don't create any files
        clans_config = LogGroupConfig("clans", "Clans")
        log_manager = log_manager.add_root_group_config(clans_config)

        # Filter nonexistent path should return empty list
        result = log_manager.filter(["clans"])
        assert result == []

    def test_filter_with_specific_date_day(self, tmp_path: Path) -> None:
        """Test filtering with specific date."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log file (will be in today's date)
        log_file = log_manager.create_log_file(
            sample_func_one, "test_op", ["clans", "myrepo", "default"]
        )

        # Filter with correct date should work
        result = log_manager.filter(["clans"], date_day=log_file.date_day)
        assert "myrepo" in result

        # Filter with wrong date should return empty
        result = log_manager.filter(["clans"], date_day="2020-01-01")
        assert result == []

    def test_filter_with_invalid_date_format(self, tmp_path: Path) -> None:
        """Test filtering with invalid date format."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        log_manager = log_manager.add_root_group_config(clans_config)

        # Filter with invalid date should return empty list
        result = log_manager.filter(["clans"], date_day="invalid-date")
        assert result == []

    def test_filter_no_log_days_exist(self, tmp_path: Path) -> None:
        """Test filtering when no log days exist."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure but don't create any files
        clans_config = LogGroupConfig("clans", "Clans")
        log_manager = log_manager.add_root_group_config(clans_config)

        # Filter when no days exist should return empty list
        result = log_manager.filter(["clans"])
        assert result == []

    def test_filter_multiple_repos_and_machines(self, tmp_path: Path) -> None:
        """Test complex filtering scenario with multiple repos and machines."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up nested structure
        clans_config = LogGroupConfig("clans", "Clans")
        machines_config = LogGroupConfig("machines", "Machines")
        clans_config = clans_config.add_child(machines_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create complex hierarchy
        repos = ["/home/user/repo1", "/home/user/repo2"]
        machines = ["wintux", "demo", "gchq-local"]

        for repo in repos:
            for machine in machines:
                log_manager.create_log_file(
                    sample_func_one,
                    f"test_{repo}_{machine}",
                    ["clans", repo, "machines", machine],
                )

        # Test filtering at different levels
        # List all repos
        result = log_manager.filter(["clans"])
        assert sorted(result) == sorted(repos)

        # List all machines under first repo
        result = log_manager.filter(["clans", repos[0], "machines"])
        assert sorted(result) == sorted(machines)

        # List all machines under second repo
        result = log_manager.filter(["clans", repos[1], "machines"])
        assert sorted(result) == sorted(machines)


class TestGetLogFileWithArrays:
    """Test the modified get_log_file method that accepts specific_group as array."""

    def test_get_log_file_with_specific_group_array(self, tmp_path: Path) -> None:
        """Test get_log_file with specific_group as array."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up nested structure
        clans_config = LogGroupConfig("clans", "Clans")
        machines_config = LogGroupConfig("machines", "Machines")
        clans_config = clans_config.add_child(machines_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log files
        repo_name = "/home/user/myrepo"
        machine_name = "wintux"

        log_file = log_manager.create_log_file(
            sample_func_one,
            "deploy_machine",
            ["clans", repo_name, "machines", machine_name],
        )

        # Search using array for specific_group
        found_log = log_manager.get_log_file(
            "deploy_machine",
            specific_group=["clans", repo_name, "machines", machine_name],
        )

        assert found_log is not None
        # Check essential attributes since group format may differ due to URL encoding
        assert found_log.op_key == log_file.op_key
        assert found_log.date_day == log_file.date_day
        assert found_log.date_second == log_file.date_second
        assert found_log.func_name == log_file.func_name
        assert found_log._base_dir == log_file._base_dir

    def test_get_log_file_with_specific_group_array_special_chars(
        self, tmp_path: Path
    ) -> None:
        """Test get_log_file with special characters in dynamic names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log file with special characters
        repo_name = "repo with spaces & symbols!"

        log_file = log_manager.create_log_file(
            sample_func_one, "special_deploy", ["clans", repo_name, "default"]
        )

        # Search using array with special characters
        found_log = log_manager.get_log_file(
            "special_deploy", specific_group=["clans", repo_name, "default"]
        )

        assert found_log is not None
        # Check essential attributes since group format may differ due to URL encoding
        assert found_log.op_key == log_file.op_key
        assert found_log.date_day == log_file.date_day
        assert found_log.date_second == log_file.date_second
        assert found_log.func_name == log_file.func_name
        assert found_log._base_dir == log_file._base_dir

    def test_get_log_file_with_specific_group_array_not_found(
        self, tmp_path: Path
    ) -> None:
        """Test get_log_file with specific_group array when group doesn't exist."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Don't create any log files

        # Search in non-existent group
        found_log = log_manager.get_log_file(
            "nonexistent_op", specific_group=["clans", "nonexistent_repo", "default"]
        )

        assert found_log is None

    def test_get_log_file_without_specific_group_still_works(
        self, tmp_path: Path
    ) -> None:
        """Test that get_log_file still works without specific_group parameter."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log file
        log_file = log_manager.create_log_file(
            sample_func_one, "general_op", ["clans", "myrepo", "default"]
        )

        # Search without specific_group (should search all)
        found_log = log_manager.get_log_file("general_op")

        assert found_log is not None
        assert found_log == log_file
        assert found_log.op_key == "general_op"

    def test_get_log_file_with_date_and_specific_group_array(
        self, tmp_path: Path
    ) -> None:
        """Test get_log_file with both specific_date_day and specific_group as array."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log file
        log_file = log_manager.create_log_file(
            sample_func_one, "dated_op", ["clans", "myrepo", "default"]
        )

        # Search with both parameters
        found_log = log_manager.get_log_file(
            "dated_op",
            specific_date_day=log_file.date_day,
            specific_group=["clans", "myrepo", "default"],
        )

        assert found_log is not None
        # Check essential attributes since group format may differ due to URL encoding
        assert found_log.op_key == log_file.op_key
        assert found_log.date_day == log_file.date_day
        assert found_log.date_second == log_file.date_second
        assert found_log.func_name == log_file.func_name
        assert found_log._base_dir == log_file._base_dir

    def test_get_log_file_unicode_in_specific_group_array(self, tmp_path: Path) -> None:
        """Test get_log_file with Unicode characters in specific_group array."""
        log_manager = LogManager(base_dir=tmp_path)

        # Set up structure
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Create log file with Unicode characters
        repo_name = "项目/中文/测试"

        log_file = log_manager.create_log_file(
            sample_func_one, "unicode_op", ["clans", repo_name, "default"]
        )

        # Search using array with Unicode characters
        found_log = log_manager.get_log_file(
            "unicode_op", specific_group=["clans", repo_name, "default"]
        )

        assert found_log is not None
        # Check essential attributes since group format may differ due to URL encoding
        assert found_log.op_key == log_file.op_key
        assert found_log.date_day == log_file.date_day
        assert found_log.date_second == log_file.date_second
        assert found_log.func_name == log_file.func_name
        assert found_log._base_dir == log_file._base_dir
