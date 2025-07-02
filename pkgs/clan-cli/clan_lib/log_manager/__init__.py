import datetime
import logging
import urllib.parse
from collections.abc import Callable  # Union for str | None
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path

log = logging.getLogger(__name__)


# Global helper function for format checking (used by LogManager and internally by classes)
def is_correct_day_format(date_day: str) -> bool:
    """Check if the date_day is in the correct format YYYY-MM-DD."""
    try:
        datetime.datetime.strptime(date_day, "%Y-%m-%d").replace(tzinfo=datetime.UTC)
    except ValueError:
        return False
    return True


@total_ordering
@dataclass(frozen=True)
class LogFile:
    op_key: str
    date_day: str  # YYYY-MM-DD
    group: str
    func_name: str
    _base_dir: Path
    date_second: str  # HH-MM-SS

    def __post_init__(self) -> None:
        # Validate formats upon initialization.
        if not is_correct_day_format(self.date_day):
            msg = f"LogFile.date_day '{self.date_day}' is not in YYYY-MM-DD format."
            raise ValueError(msg)
        try:
            datetime.datetime.strptime(self.date_second, "%H-%M-%S").replace(
                tzinfo=datetime.UTC
            )
        except ValueError as ex:
            msg = f"LogFile.date_second '{self.date_second}' is not in HH-MM-SS format."
            raise ValueError(msg) from ex

    @property
    def _datetime_obj(self) -> datetime.datetime:
        # Formats are pre-validated by __post_init__.
        return datetime.datetime.strptime(
            f"{self.date_day} {self.date_second}", "%Y-%m-%d %H-%M-%S"
        ).replace(tzinfo=datetime.UTC)

    @classmethod
    def from_path(cls, file: Path) -> "LogFile":
        date_day = file.parent.parent.parent.name
        group = urllib.parse.unquote(file.parent.parent.name)
        func_name = file.parent.name
        base_dir = file.parent.parent.parent.parent

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

    def get_file_path(self) -> Path:
        return (
            self._base_dir
            / self.date_day
            / urllib.parse.quote(self.group, safe="")
            / self.func_name
            / f"{self.date_second}_{self.op_key}.log"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogFile):
            return NotImplemented
        # Compare all significant fields for equality
        return (
            self._datetime_obj == other._datetime_obj
            and self.group == other.group
            and self.func_name == other.func_name
            and self.op_key == other.op_key
            and self._base_dir == other._base_dir
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogFile):
            return NotImplemented
        # Primary sort: datetime (newest first). self is "less than" other if self is newer.
        if self._datetime_obj != other._datetime_obj:
            return self._datetime_obj > other._datetime_obj
        # Secondary sort: group (alphabetical ascending)
        if self.group != other.group:
            return self.group < other.group
        # Tertiary sort: func_name (alphabetical ascending)
        if self.func_name != other.func_name:
            return self.func_name < other.func_name
        # Quaternary sort: op_key (alphabetical ascending)
        return self.op_key < other.op_key


@total_ordering
@dataclass(frozen=True)
class LogFuncDir:
    date_day: str
    group: str
    func_name: str
    _base_dir: Path

    def __post_init__(self) -> None:
        if not is_correct_day_format(self.date_day):
            msg = f"LogFuncDir.date_day '{self.date_day}' is not in YYYY-MM-DD format."
            raise ValueError(msg)

    @property
    def _date_obj(self) -> datetime.date:
        return (
            datetime.datetime.strptime(self.date_day, "%Y-%m-%d")
            .replace(tzinfo=datetime.UTC)
            .date()
        )

    def get_dir_path(self) -> Path:
        return (
            self._base_dir
            / self.date_day
            / urllib.parse.quote(self.group, safe="")
            / self.func_name
        )

    def get_log_files(self) -> list[LogFile]:
        dir_path = self.get_dir_path()
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        log_files_list: list[LogFile] = []
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix == ".log":
                try:
                    log_files_list.append(LogFile.from_path(file_path))
                except ValueError:
                    log.warning(
                        f"Skipping malformed log file '{file_path.name}' in '{dir_path}'."
                    )

        return sorted(log_files_list)  # Sorts using LogFile.__lt__ (newest first)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogFuncDir):
            return NotImplemented
        return (
            self.date_day == other.date_day
            and self.group == other.group
            and self.func_name == other.func_name
            and self._base_dir == other._base_dir
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogFuncDir):
            return NotImplemented
        # Primary sort: date (newest first)
        if self._date_obj != other._date_obj:
            return self._date_obj > other._date_obj
        # Secondary sort: group (alphabetical ascending)
        if self.group != other.group:
            return self.group < other.group
        # Tertiary sort: func_name (alphabetical ascending)
        return self.func_name < other.func_name


@total_ordering
@dataclass(frozen=True)
class LogGroupDir:
    date_day: str
    group: str
    _base_dir: Path

    def __post_init__(self) -> None:
        if not is_correct_day_format(self.date_day):
            msg = f"LogGroupDir.date_day '{self.date_day}' is not in YYYY-MM-DD format."
            raise ValueError(msg)

    @property
    def _date_obj(self) -> datetime.date:
        return (
            datetime.datetime.strptime(self.date_day, "%Y-%m-%d")
            .replace(tzinfo=datetime.UTC)
            .date()
        )

    def get_dir_path(self) -> Path:
        return self._base_dir / self.date_day / urllib.parse.quote(self.group, safe="")

    def get_log_files(self) -> list[LogFuncDir]:
        dir_path = self.get_dir_path()
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        func_dirs_list: list[LogFuncDir] = []
        for func_dir_path in dir_path.iterdir():
            if func_dir_path.is_dir():
                try:
                    func_dirs_list.append(
                        LogFuncDir(
                            date_day=self.date_day,
                            group=self.group,
                            func_name=func_dir_path.name,
                            _base_dir=self._base_dir,
                        )
                    )
                except ValueError:
                    log.warning(
                        f"Skipping malformed function directory '{func_dir_path.name}' in '{dir_path}'."
                    )

        return sorted(func_dirs_list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogGroupDir):
            return NotImplemented
        return (
            self.date_day == other.date_day
            and self.group == other.group
            and self._base_dir == other._base_dir
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogGroupDir):
            return NotImplemented
        # Primary sort: date (newest first)
        if self._date_obj != other._date_obj:
            return self._date_obj > other._date_obj
        # Secondary sort: group (alphabetical ascending)
        return self.group < other.group


@total_ordering
@dataclass(frozen=True)
class LogDayDir:
    date_day: str
    _base_dir: Path

    def __post_init__(self) -> None:
        if not is_correct_day_format(self.date_day):
            msg = f"LogDayDir.date_day '{self.date_day}' is not in YYYY-MM-DD format."
            raise ValueError(msg)

    @property
    def _date_obj(self) -> datetime.date:
        return (
            datetime.datetime.strptime(self.date_day, "%Y-%m-%d")
            .replace(tzinfo=datetime.UTC)
            .date()
        )

    def get_dir_path(self) -> Path:
        return self._base_dir / self.date_day

    def get_log_files(self) -> list[LogGroupDir]:
        dir_path = self.get_dir_path()
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        group_dirs_list: list[LogGroupDir] = []

        # First level: group directories
        for group_dir_path in dir_path.iterdir():
            if group_dir_path.is_dir():
                group_name = urllib.parse.unquote(group_dir_path.name)
                try:
                    group_dirs_list.append(
                        LogGroupDir(
                            date_day=self.date_day,
                            group=group_name,
                            _base_dir=self._base_dir,
                        )
                    )
                except ValueError:
                    log.warning(
                        f"Warning: Skipping malformed group directory '{group_dir_path.name}' in '{dir_path}'."
                    )
        return sorted(group_dirs_list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogDayDir):
            return NotImplemented
        return self.date_day == other.date_day and self._base_dir == other._base_dir

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogDayDir):
            return NotImplemented
        # Primary sort: date (newest first)
        return self._date_obj > other._date_obj


@dataclass(frozen=True)
class LogManager:
    base_dir: Path

    def create_log_file(
        self, func: Callable, op_key: str, group: str | None = None
    ) -> LogFile:
        now_utc = datetime.datetime.now(tz=datetime.UTC)

        if group is None:
            group = "default"

        log_file = LogFile(
            op_key=op_key,
            date_day=now_utc.strftime("%Y-%m-%d"),
            group=group,
            date_second=now_utc.strftime("%H-%M-%S"),  # Corrected original's %H-$M-%S
            func_name=func.__name__,
            _base_dir=self.base_dir,
        )

        log_path = log_file.get_file_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if log_path.exists():
            msg = f"BUG! Log file {log_path} already exists."
            raise FileExistsError(msg)

        log_path.touch()
        return log_file

    def list_log_days(self) -> list[LogDayDir]:
        if not self.base_dir.exists() or not self.base_dir.is_dir():
            return []

        log_day_dirs_list: list[LogDayDir] = []
        for day_dir_candidate_path in self.base_dir.iterdir():
            if day_dir_candidate_path.is_dir() and is_correct_day_format(
                day_dir_candidate_path.name
            ):
                try:
                    log_day_dirs_list.append(
                        LogDayDir(
                            date_day=day_dir_candidate_path.name,
                            _base_dir=self.base_dir,
                        )
                    )
                except ValueError:
                    log.warning(
                        f"Skipping directory with invalid date format '{day_dir_candidate_path.name}'."
                    )

        return sorted(log_day_dirs_list)  # Sorts using LogDayDir.__lt__ (newest first)

    def get_log_file(
        self,
        op_key_to_find: str,
        specific_date_day: str | None = None,
        specific_group: str | None = None,
    ) -> LogFile | None:
        days_to_search: list[LogDayDir]

        if specific_date_day:
            if not is_correct_day_format(specific_date_day):
                # print(f"Warning: Provided specific_date_day '{specific_date_day}' is not in YYYY-MM-DD format.")
                return None
            try:
                target_day_dir = LogDayDir(
                    date_day=specific_date_day, _base_dir=self.base_dir
                )
                if (
                    not target_day_dir.get_dir_path().exists()
                ):  # Check if dir exists on disk
                    return None
                days_to_search = [target_day_dir]  # Search only this specific day
            except ValueError:  # If LogDayDir construction fails (e.g. date_day format despite is_correct_day_format)
                return None
        else:
            days_to_search = self.list_log_days()  # Already sorted, newest day first

        for day_dir in (
            days_to_search
        ):  # Iterates newest day first if days_to_search came from list_log_days()
            # day_dir.get_log_files() returns List[LogGroupDir], sorted by group name
            for group_dir in day_dir.get_log_files():
                # Skip this group if specific_group is provided and doesn't match
                if specific_group is not None and group_dir.group != specific_group:
                    continue

                # group_dir.get_log_files() returns List[LogFuncDir], sorted by func_name
                for func_dir in group_dir.get_log_files():
                    # func_dir.get_log_files() returns List[LogFile], sorted newest file first
                    for log_file in func_dir.get_log_files():
                        if log_file.op_key == op_key_to_find:
                            return log_file
        return None
