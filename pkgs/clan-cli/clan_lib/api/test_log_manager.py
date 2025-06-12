# ruff: noqa: SLF001
import datetime
import logging  # For LogManager if not already imported
from pathlib import Path
from typing import Any  # Added Dict

import pytest

# Assuming your classes are in a file named 'log_manager_module.py'
# If they are in the same file as the tests, you don't need this relative import.
from .log_manager import (
    LogDayDir,
    LogFile,
    LogFuncDir,
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
    # Func A
    lf1 = log_manager.create_log_file(sample_func_one, "op_key_A1")  # 10-00-00
    created_files["lf1"] = lf1
    lf2 = log_manager.create_log_file(sample_func_one, "op_key_A2")  # 10-01-01
    created_files["lf2"] = lf2
    # Func B
    lf3 = log_manager.create_log_file(sample_func_two, "op_key_B1")  # 10-02-02
    created_files["lf3"] = lf3

    # Day 2: 2023-10-27 (by advancing mock time enough)
    MockDateTime._now_val = datetime.datetime(
        2023, 10, 27, 12, 0, 0, tzinfo=datetime.UTC
    )
    MockDateTime._delta = datetime.timedelta(seconds=0)  # Reset delta for new day

    lf4 = log_manager.create_log_file(sample_func_one, "op_key_A3_day2")  # 12-00-00
    created_files["lf4"] = lf4

    # Create a malformed file and dir to test skipping
    malformed_day_dir = base_dir / "2023-13-01"  # Invalid date
    malformed_day_dir.mkdir(parents=True, exist_ok=True)
    (malformed_day_dir / "some_func").mkdir(exist_ok=True)

    malformed_func_dir = base_dir / "2023-10-26" / "malformed_func_dir_name!"
    malformed_func_dir.mkdir(parents=True, exist_ok=True)

    malformed_log_file_dir = base_dir / "2023-10-26" / sample_func_one.__name__
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
        lf = LogFile("op1", "2023-10-26", "my_func", tmp_path, "10-20-30")
        assert lf.op_key == "op1"
        assert lf.date_day == "2023-10-26"
        assert lf.func_name == "my_func"
        assert lf._base_dir == tmp_path
        assert lf.date_second == "10-20-30"

    def test_creation_invalid_date_day(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in YYYY-MM-DD format"):
            LogFile("op1", "2023/10/26", "my_func", tmp_path, "10-20-30")

    def test_creation_invalid_date_second(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in HH-MM-SS format"):
            LogFile("op1", "2023-10-26", "my_func", tmp_path, "10:20:30")

    def test_datetime_obj(self, tmp_path: Path) -> None:
        lf = LogFile("op1", "2023-10-26", "my_func", tmp_path, "10-20-30")
        expected_dt = datetime.datetime(2023, 10, 26, 10, 20, 30, tzinfo=datetime.UTC)
        assert lf._datetime_obj == expected_dt

    def test_from_path_valid(self, tmp_path: Path) -> None:
        base = tmp_path / "logs"
        file_path = base / "2023-10-26" / "my_func" / "10-20-30_op_key_123.log"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        lf = LogFile.from_path(file_path)
        assert lf.op_key == "op_key_123"
        assert lf.date_day == "2023-10-26"
        assert lf.func_name == "my_func"
        assert lf._base_dir == base
        assert lf.date_second == "10-20-30"

    def test_from_path_invalid_filename_format(self, tmp_path: Path) -> None:
        file_path = (
            tmp_path / "logs" / "2023-10-26" / "my_func" / "10-20-30-op_key_123.log"
        )  # Extra dash
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        with pytest.raises(ValueError, match="is not in HH-MM-SS format."):
            LogFile.from_path(file_path)

    def test_from_path_filename_no_op_key(self, tmp_path: Path) -> None:
        file_path = tmp_path / "logs" / "2023-10-26" / "my_func" / "10-20-30_.log"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        # This will result in op_key being ""
        lf = LogFile.from_path(file_path)
        assert lf.op_key == ""

    def test_get_file_path(self, tmp_path: Path) -> None:
        lf = LogFile("op1", "2023-10-26", "my_func", tmp_path, "10-20-30")
        expected_path = tmp_path / "2023-10-26" / "my_func" / "10-20-30_op1.log"
        assert lf.get_file_path() == expected_path

    def test_equality(self, tmp_path: Path) -> None:
        lf1 = LogFile("op1", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf2 = LogFile("op1", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf3 = LogFile(
            "op2", "2023-10-26", "func_a", tmp_path, "10-00-00"
        )  # Diff op_key
        lf4 = LogFile("op1", "2023-10-26", "func_a", tmp_path, "10-00-01")  # Diff time
        assert lf1 == lf2
        assert lf1 != lf3
        assert lf1 != lf4
        assert lf1 != "not a logfile"

    def test_ordering(self, tmp_path: Path) -> None:
        # Newest datetime first
        lf_newest = LogFile("op", "2023-10-26", "f", tmp_path, "10-00-01")
        lf_older = LogFile("op", "2023-10-26", "f", tmp_path, "10-00-00")
        lf_oldest_d = LogFile("op", "2023-10-25", "f", tmp_path, "12-00-00")

        # Same datetime, different func_name (alphabetical)
        lf_func_a = LogFile("op", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf_func_b = LogFile("op", "2023-10-26", "func_b", tmp_path, "10-00-00")

        # Same datetime, same func_name, different op_key (alphabetical)
        lf_op_a = LogFile("op_a", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf_op_b = LogFile("op_b", "2023-10-26", "func_a", tmp_path, "10-00-00")

        assert lf_newest < lf_older  # lf_newest is "less than" because it's newer
        assert lf_older < lf_oldest_d

        assert lf_func_a < lf_func_b
        assert not (lf_func_b < lf_func_a)

        assert lf_op_a < lf_op_b
        assert not (lf_op_b < lf_op_a)

        # Test sorting
        files = [
            lf_older,
            lf_op_b,
            lf_newest,
            lf_func_a,
            lf_oldest_d,
            lf_op_a,
            lf_func_b,
        ]
        # Expected order (newest first, then func_name, then op_key):
        # 1. lf_newest (2023-10-26 10:00:01 func_f op)
        # 2. lf_func_a (2023-10-26 10:00:00 func_a op) - same time as lf_older, but func_a < func_f
        # 3. lf_op_a   (2023-10-26 10:00:00 func_a op_a)
        # 4. lf_op_b   (2023-10-26 10:00:00 func_a op_b)
        # 5. lf_func_b (2023-10-26 10:00:00 func_b op)
        # 6. lf_older  (2023-10-26 10:00:00 func_f op)
        # 7. lf_oldest_d(2023-10-25 12:00:00 func_f op)

        sorted(files)
        # Let's re-evaluate based on rules:
        # lf_func_a is same time as lf_older. func_a < f. So lf_func_a < lf_older.
        # lf_op_a is same time and func as lf_func_a. op_a > op. So lf_func_a < lf_op_a.

        lf_fa_op = LogFile("op", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf_fa_opa = LogFile("op_a", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf_fa_opb = LogFile("op_b", "2023-10-26", "func_a", tmp_path, "10-00-00")
        lf_fb_op = LogFile("op", "2023-10-26", "func_b", tmp_path, "10-00-00")
        lf_ff_op1 = LogFile("op", "2023-10-26", "f", tmp_path, "10-00-01")  # lf_newest
        lf_ff_op0 = LogFile("op", "2023-10-26", "f", tmp_path, "10-00-00")  # lf_older
        lf_old_day = LogFile(
            "op", "2023-10-25", "f", tmp_path, "12-00-00"
        )  # lf_oldest_d

        files_redefined = [
            lf_fa_op,
            lf_fa_opa,
            lf_fa_opb,
            lf_fb_op,
            lf_ff_op1,
            lf_ff_op0,
            lf_old_day,
        ]
        sorted_redefined = sorted(files_redefined)

        expected_redefined = [
            lf_ff_op1,  # Newest time
            lf_ff_op0,  # 2023-10-26 10:00:00, f,      op
            lf_fa_op,  # 2023-10-26 10:00:00, func_a, op (func_a smallest)
            lf_fa_opa,  # 2023-10-26 10:00:00, func_a, op_a
            lf_fa_opb,  # 2023-10-26 10:00:00, func_a, op_b
            lf_fb_op,  # 2023-10-26 10:00:00, func_b, op
            lf_old_day,
        ]

        assert sorted_redefined == expected_redefined


# --- Tests for LogFuncDir ---


class TestLogFuncDir:
    def test_creation_valid(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "my_func", tmp_path)
        assert lfd.date_day == "2023-10-26"
        assert lfd.func_name == "my_func"
        assert lfd._base_dir == tmp_path

    def test_creation_invalid_date_day(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not in YYYY-MM-DD format"):
            LogFuncDir("2023/10/26", "my_func", tmp_path)

    def test_date_obj(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "my_func", tmp_path)
        assert lfd._date_obj == datetime.date(2023, 10, 26)

    def test_get_dir_path(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "my_func", tmp_path)
        expected = tmp_path / "2023-10-26" / "my_func"
        assert lfd.get_dir_path() == expected

    def test_get_log_files_empty_or_missing(self, tmp_path: Path) -> None:
        lfd = LogFuncDir("2023-10-26", "non_existent_func", tmp_path)
        assert lfd.get_log_files() == []  # Dir does not exist

        dir_path = lfd.get_dir_path()
        dir_path.mkdir(parents=True, exist_ok=True)  # Dir exists but empty
        assert lfd.get_log_files() == []

    def test_get_log_files_populated(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        base = tmp_path
        lfd = LogFuncDir("2023-10-26", "my_func", base)
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

        # Expected order: newest first (10-00-00_op1, then 10-00-00_op0, then 09-00-00_op2)
        # Sorting by LogFile: newest datetime first, then func_name (same here), then op_key
        expected_lf1 = LogFile.from_path(lf1_path)
        expected_lf2 = LogFile.from_path(lf2_path)
        expected_lf3 = LogFile.from_path(lf3_path)

        assert log_files[0] == expected_lf1  # 10-00-00_op1
        assert log_files[1] == expected_lf3  # 10-00-00_op0 (op0 < op1)
        assert log_files[2] == expected_lf2  # 09-00-00_op2

    def test_equality(self, tmp_path: Path) -> None:
        lfd1 = LogFuncDir("2023-10-26", "func_a", tmp_path)
        lfd2 = LogFuncDir("2023-10-26", "func_a", tmp_path)
        lfd3 = LogFuncDir("2023-10-27", "func_a", tmp_path)  # Diff date
        lfd4 = LogFuncDir("2023-10-26", "func_b", tmp_path)  # Diff func_name
        assert lfd1 == lfd2
        assert lfd1 != lfd3
        assert lfd1 != lfd4
        assert lfd1 != "not a logfuncdir"

    def test_ordering(self, tmp_path: Path) -> None:
        # Newest date first
        lfd_new_date = LogFuncDir("2023-10-27", "func_a", tmp_path)
        lfd_old_date = LogFuncDir("2023-10-26", "func_a", tmp_path)

        # Same date, different func_name (alphabetical)
        lfd_func_a = LogFuncDir("2023-10-26", "func_a", tmp_path)
        lfd_func_b = LogFuncDir("2023-10-26", "func_b", tmp_path)

        assert (
            lfd_new_date < lfd_old_date
        )  # lfd_new_date is "less than" because it's newer
        assert lfd_func_a < lfd_func_b

        # Expected sort: lfd_new_date, then lfd_func_a, then lfd_func_b, then lfd_old_date (if func_a different)
        # but lfd_old_date and lfd_func_a are same date.
        # Expected: lfd_new_date, then lfd_func_a (same date as old_date but func_a<func_a is false, it's equal so goes by obj id or first seen?)
        # Ok, LogFuncDir same date, sort by func_name. lfd_old_date is func_a.
        # So: lfd_new_date (2023-10-27, func_a)
        #     lfd_func_a (2023-10-26, func_a)
        #     lfd_old_date (2023-10-26, func_a) -- wait, lfd_func_a IS lfd_old_date content-wise if func_name 'func_a'
        #     lfd_func_b (2023-10-26, func_b)

        # Redefine for clarity
        lfd1 = LogFuncDir("2023-10-27", "z_func", tmp_path)  # Newest date
        lfd2 = LogFuncDir(
            "2023-10-26", "a_func", tmp_path
        )  # Older date, alpha first func
        lfd3 = LogFuncDir(
            "2023-10-26", "b_func", tmp_path
        )  # Older date, alpha second func

        items_redefined = [lfd3, lfd1, lfd2]
        sorted_items = sorted(items_redefined)
        expected_sorted = [lfd1, lfd2, lfd3]
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

        # Create func dirs
        func_a_path = day_dir_path / "func_a"
        func_a_path.mkdir()
        func_b_path = day_dir_path / "func_b"
        func_b_path.mkdir()

        # Create a non-dir and a malformed func dir name (if your logic would try to parse it)
        (day_dir_path / "not_a_dir.txt").touch()
        # LogDayDir's get_log_files doesn't try to parse func dir names for validity beyond being a dir
        # The warning in LogDayDir.get_log_files is for ValueError from LogFuncDir init
        # which can only happen if self.date_day is bad, but it's validated in LogDayDir.__post_init__.
        # So, the warning there is unlikely to trigger from func_dir_path.name issues.

        with caplog.at_level(logging.WARNING):
            log_func_dirs = ldd.get_log_files()

        assert len(log_func_dirs) == 2
        # No warnings expected from this specific setup for LogDayDir.get_log_files
        # assert not any("Skipping malformed function directory" in record.message for record in caplog.records)

        # Expected order: func_name alphabetical (since date_day is the same for all)
        expected_lfd_a = LogFuncDir("2023-10-26", "func_a", base)
        expected_lfd_b = LogFuncDir("2023-10-26", "func_b", base)

        assert log_func_dirs[0] == expected_lfd_a
        assert log_func_dirs[1] == expected_lfd_b

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
