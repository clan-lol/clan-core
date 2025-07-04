import datetime
import logging
import urllib.parse
from collections.abc import Callable  # Union for str | None
from dataclasses import dataclass, field
from functools import total_ordering
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LogGroupConfig:
    """Configuration for a hierarchical log group with nickname support."""

    name: str  # The name of this group level (single directory name)
    nickname: str | None = None  # Optional display name for easier visibility
    children: dict[str, "LogGroupConfig"] = field(
        default_factory=dict
    )  # Nested child groups

    def get_display_name(self) -> str:
        """Get the display name (nickname if available, otherwise the name)."""
        return self.nickname if self.nickname else self.name

    def add_child(self, child: "LogGroupConfig") -> "LogGroupConfig":
        """Add a child group configuration and return a new LogGroupConfig instance."""
        new_children = {**self.children, child.name: child}
        return LogGroupConfig(
            name=self.name, nickname=self.nickname, children=new_children
        )

    def get_child(self, name: str) -> "LogGroupConfig | None":
        """Get a child group by name."""
        return self.children.get(name)

    def get_path_components(self) -> list[str]:
        """Get the path components for this group (just the name as a single component)."""
        return [self.name]


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
        # Work backwards from the file path to reconstruct the hierarchical group structure
        func_name = file.parent.name

        # Traverse up from func_dir to find the date_day directory
        current_path = file.parent.parent  # Start from group level
        group_components: list[str] = []

        while (
            current_path.parent.name != current_path.parent.parent.name
        ):  # Until we reach base_dir
            parent_name = current_path.name
            # Check if this looks like a date directory (YYYY-MM-DD format)
            if is_correct_day_format(parent_name):
                date_day = parent_name
                base_dir = current_path.parent
                break
            # This is a group component, URL decode it
            group_components.insert(0, urllib.parse.unquote(parent_name))
            current_path = current_path.parent
        else:
            # Fallback: assume single-level structure
            date_day = file.parent.parent.parent.name
            group_components = [urllib.parse.unquote(file.parent.parent.name)]
            base_dir = file.parent.parent.parent.parent

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

    def get_file_path(self) -> Path:
        # Create nested directory structure for hierarchical groups
        path = self._base_dir / self.date_day

        # Split group by slash and create nested directories
        # Dynamic elements are already URL encoded at LogFile creation time
        group_components = self.group.split("/")
        for component in group_components:
            path = path / component

        return path / self.func_name / f"{self.date_second}_{self.op_key}.log"

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
        # Create nested directory structure for hierarchical groups
        path = self._base_dir / self.date_day

        # Split group by slash and create nested directories
        # Dynamic elements are already URL encoded at LogFile creation time
        group_components = self.group.split("/")
        for component in group_components:
            path = path / component

        return path / self.func_name

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
    group_path: list[
        str
    ]  # Path components for nested groups, e.g., ["flakes", "flake1", "machines"]
    _base_dir: Path
    nickname: str | None = None

    @property
    def group_name(self) -> str:
        """Get the name of this group level (last component of path)."""
        return self.group_path[-1] if self.group_path else ""

    @property
    def full_group_path(self) -> str:
        """Get the full group path as a slash-separated string."""
        return "/".join(self.group_path)

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
        """Get the directory path for this nested group."""
        path = self._base_dir / self.date_day
        for i, component in enumerate(self.group_path):
            if i % 2 == 1:  # Odd index = dynamic element, needs URL encoding
                path = path / urllib.parse.quote(component, safe="")
            else:  # Even index = structure element, no encoding needed
                path = path / component
        return path

    def get_display_name(self) -> str:
        """Get the display name (nickname if available, otherwise group name)."""
        return self.nickname if self.nickname else self.group_name

    def get_nested_groups(self) -> list["LogGroupDir"]:
        """Get nested LogGroupDir instances within this group."""
        dir_path = self.get_dir_path()
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        nested_groups: list[LogGroupDir] = []
        for subdir_path in dir_path.iterdir():
            if subdir_path.is_dir():
                # Check if this is a group directory (contains other groups) or a function directory
                # Function directories should contain .log files, group directories should contain other directories
                contains_log_files = any(
                    f.suffix == ".log"
                    for f in subdir_path.rglob("*.log")
                    if f.parent == subdir_path
                )
                contains_subdirs = any(p.is_dir() for p in subdir_path.iterdir())

                # If it contains subdirectories but no direct log files, it's likely a nested group
                if contains_subdirs and not contains_log_files:
                    group_name = urllib.parse.unquote(subdir_path.name)
                    nested_path = [*self.group_path, group_name]
                    nested_groups.append(
                        LogGroupDir(
                            date_day=self.date_day,
                            group_path=nested_path,
                            _base_dir=self._base_dir,
                            nickname=None,  # Will be populated by LogManager if configured
                        )
                    )

        return sorted(nested_groups)

    def get_log_files(self) -> list[LogFuncDir]:
        dir_path = self.get_dir_path()
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        func_dirs_list: list[LogFuncDir] = []
        for func_dir_path in dir_path.iterdir():
            if func_dir_path.is_dir():
                # Only include directories that actually contain log files (function directories)
                # Skip directories that contain other directories (nested groups)
                contains_log_files = any(
                    f.suffix == ".log" for f in func_dir_path.iterdir() if f.is_file()
                )
                if contains_log_files:
                    try:
                        func_dirs_list.append(
                            LogFuncDir(
                                date_day=self.date_day,
                                group=self.full_group_path,
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
            and self.group_path == other.group_path
            and self._base_dir == other._base_dir
            and self.nickname == other.nickname
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogGroupDir):
            return NotImplemented
        # Primary sort: date (newest first)
        if self._date_obj != other._date_obj:
            return self._date_obj > other._date_obj
        # Secondary sort: group path (alphabetical ascending)
        return self.group_path < other.group_path


@total_ordering
@dataclass(frozen=True)
class LogDayDir:
    date_day: str
    _base_dir: Path
    group_configs: dict[str, LogGroupConfig] = field(default_factory=dict)

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

    def get_root_groups(self) -> list[LogGroupDir]:
        """Get root-level LogGroupDir instances."""
        return self._get_groups_at_path([])

    def _get_groups_at_path(self, current_path: list[str]) -> list[LogGroupDir]:
        # Build the current directory path
        dir_path = self._base_dir / self.date_day
        for i, component in enumerate(current_path):
            if i % 2 == 1:  # Odd index = dynamic element, needs URL encoding
                dir_path = dir_path / urllib.parse.quote(component, safe="")
            else:  # Even index = structure element, no encoding needed
                dir_path = dir_path / component

        if not dir_path.exists() or not dir_path.is_dir():
            return []

        group_dirs_list: list[LogGroupDir] = []

        # Look for group directories at this level
        for subdir_path in dir_path.iterdir():
            if subdir_path.is_dir():
                group_name = urllib.parse.unquote(subdir_path.name)
                group_path = [*current_path, group_name]

                # A directory is a group directory if:
                # 1. It contains function directories (directories with .log files), OR
                # 2. It contains other group directories (nested structure)
                # 3. It's NOT itself a function directory (doesn't contain .log files directly)

                is_function_dir = self._is_function_directory(subdir_path)

                if not is_function_dir:  # Not a function directory
                    contains_functions = self._contains_function_directories(
                        subdir_path
                    )
                    contains_groups = self._contains_group_directories(subdir_path)

                    # If it contains either functions or groups, it's a valid group directory
                    if contains_functions or contains_groups:
                        try:
                            # Find nickname from configuration
                            nickname = None
                            config = self._find_config_for_path(group_path)
                            if config:
                                nickname = config.nickname

                            group_dirs_list.append(
                                LogGroupDir(
                                    date_day=self.date_day,
                                    group_path=group_path,
                                    _base_dir=self._base_dir,
                                    nickname=nickname,
                                )
                            )
                        except ValueError:
                            log.warning(
                                f"Warning: Skipping malformed group directory '{subdir_path.name}' in '{dir_path}'."
                            )

        return sorted(group_dirs_list)

    def _contains_function_directories(self, dir_path: Path) -> bool:
        """Check if directory contains function directories (directories with .log files)."""
        for subdir in dir_path.iterdir():
            if subdir.is_dir():
                # Check if this subdirectory contains .log files directly
                if any(f.suffix == ".log" for f in subdir.iterdir() if f.is_file()):
                    return True
        return False

    def _is_function_directory(self, dir_path: Path) -> bool:
        """Check if a directory is a function directory (contains .log files directly)."""
        return any(f.suffix == ".log" for f in dir_path.iterdir() if f.is_file())

    def _contains_group_directories(self, dir_path: Path) -> bool:
        """Check if directory contains nested group directories."""
        for subdir in dir_path.iterdir():
            if subdir.is_dir() and not self._is_function_directory(subdir):
                # If subdir is not a function directory, it might be a group directory
                return True
        return False

    def _find_config_for_path(self, group_path: list[str]) -> LogGroupConfig | None:
        """Find the configuration for a given group path."""
        if not group_path:
            return None

        current_config = self.group_configs.get(group_path[0])
        if not current_config:
            return None

        # Traverse down the hierarchy
        for component in group_path[1:]:
            current_config = current_config.get_child(component)
            if not current_config:
                return None

        return current_config

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogDayDir):
            return NotImplemented
        return (
            self.date_day == other.date_day
            and self._base_dir == other._base_dir
            and self.group_configs == other.group_configs
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LogDayDir):
            return NotImplemented
        # Primary sort: date (newest first)
        return self._date_obj > other._date_obj


@dataclass(frozen=True)
class LogManager:
    base_dir: Path
    root_group_configs: dict[str, LogGroupConfig] = field(default_factory=dict)

    def add_root_group_config(self, group_config: LogGroupConfig) -> "LogManager":
        """Return a new LogManager with the added root-level group configuration."""
        new_configs = {**self.root_group_configs, group_config.name: group_config}
        return LogManager(base_dir=self.base_dir, root_group_configs=new_configs)

    def find_group_config(self, group_path: list[str]) -> LogGroupConfig | None:
        """Find group configuration by traversing the hierarchical path.

        Only looks at structure elements (even indices), ignoring dynamic names (odd indices).
        """
        if not group_path:
            return None

        current_config = self.root_group_configs.get(group_path[0])
        if not current_config:
            return None

        # If only root group, return it
        if len(group_path) == 1:
            return current_config

        # Traverse down the hierarchy, only looking at structure elements (even indices)
        for i in range(2, len(group_path), 2):
            structure_name = group_path[i]
            current_config = current_config.get_child(structure_name)
            if not current_config:
                return None

        return current_config

    def get_group_display_name(self, group_path: list[str] | str) -> str:
        """Get the display name for a group (nickname if configured, otherwise group name).

        For alternating structure/dynamic pattern:
        - Structure elements (even indices): use configured nickname
        - Dynamic elements (odd indices): use actual name
        """
        if isinstance(group_path, str):
            group_path = group_path.split("/")

        if not group_path:
            return ""

        # Check if the last element is a structure element (even index) or dynamic element (odd index)
        last_index = len(group_path) - 1

        if last_index % 2 == 0:
            # Even index = structure element, try to find config
            config = self.find_group_config(group_path)
            if config:
                return config.get_display_name()
            # Fallback to the structure name itself
            return group_path[-1]
        # Odd index = dynamic element, return the actual name
        return group_path[-1]

    def create_nested_log_group_dir(
        self, date_day: str, group_path: list[str]
    ) -> LogGroupDir:
        """Create a LogGroupDir with nickname support if configured."""
        config = self.find_group_config(group_path)
        nickname = config.nickname if config else None

        return LogGroupDir(
            date_day=date_day,
            group_path=group_path,
            _base_dir=self.base_dir,
            nickname=nickname,
        )

    def create_log_file(
        self, func: Callable, op_key: str, group_path: list[str] | None = None
    ) -> LogFile:
        now_utc = datetime.datetime.now(tz=datetime.UTC)

        if group_path is None:
            group_path = ["default"]

        # Validate that the group path structure is registered in the configuration
        if not self._is_group_path_registered(group_path):
            group_str = "/".join(group_path)
            msg = f"Group structure '{group_str}' is not valid. Root group '{group_path[0]}' or structure elements at even indices are not registered."
            raise ValueError(msg)

        # URL encode dynamic elements (odd indices) before creating group string
        encoded_group_path = []
        for i, component in enumerate(group_path):
            if i % 2 == 1:  # Odd index = dynamic element, needs URL encoding
                encoded_group_path.append(urllib.parse.quote(component, safe=""))
            else:  # Even index = structure element, no encoding needed
                encoded_group_path.append(component)

        # Convert encoded path to string for LogFile
        group_str = "/".join(encoded_group_path)

        log_file = LogFile(
            op_key=op_key,
            date_day=now_utc.strftime("%Y-%m-%d"),
            group=group_str,
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

    def _is_group_path_registered(self, group_path: list[str]) -> bool:
        """Check if the given group path structure is registered in the configuration.

        This validates the group structure (e.g., clans/<name>/machines) but allows
        dynamic names (e.g., <name> can be any value).
        """
        # Special case: allow "default" group without registration
        if group_path == ["default"]:
            return True

        # For dynamic group validation, we need to check if the structure exists
        # by matching the pattern, not the exact path
        return self._validate_group_structure(group_path)

    def _validate_group_structure(self, group_path: list[str]) -> bool:
        """Validate that the group structure exists, allowing dynamic names.

        Pattern alternates: structure -> dynamic -> structure -> dynamic -> ...
        - Even indices (0, 2, 4, ...): must be registered group names (structure elements)
        - Odd indices (1, 3, 5, ...): can be any dynamic names (will be URL encoded)

        Examples:
        - ["clans", "repo-name", "default"] -> clans(structure) -> repo-name(dynamic) -> default(structure)
        - ["clans", "repo-name", "machines", "machine-name"] -> clans(struct) -> repo-name(dyn) -> machines(struct) -> machine-name(dyn)
        """
        if not group_path:
            return False

        # Check if root group exists (index 0 - always structure)
        root_group = group_path[0]
        if root_group not in self.root_group_configs:
            return False

        if len(group_path) == 1:
            return True

        # For longer paths, traverse the structure elements only
        current_config = self.root_group_configs[root_group]

        # Check all structure elements (even indices starting from 2)
        for i in range(2, len(group_path), 2):
            structure_name = group_path[i]

            # Look for this structure in current config's children
            if structure_name not in current_config.children:
                return False

            current_config = current_config.children[structure_name]

        return True

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
                            group_configs=self.root_group_configs,
                        )
                    )
                except ValueError:
                    log.warning(
                        f"Skipping directory with invalid date format '{day_dir_candidate_path.name}'."
                    )

        return sorted(log_day_dirs_list)  # Sorts using LogDayDir.__lt__ (newest first)

    def get_log_file(
        self,
        op_key: str,
        *,
        date_day: str | None = None,
        selector: list[str] | None = None,
    ) -> LogFile | None:
        days_to_search: list[LogDayDir]

        if date_day:
            if not is_correct_day_format(date_day):
                return None
            try:
                target_day_dir = LogDayDir(
                    date_day=date_day,
                    _base_dir=self.base_dir,
                    group_configs=self.root_group_configs,
                )
                if not target_day_dir.get_dir_path().exists():
                    return None
                days_to_search = [target_day_dir]
            except ValueError:
                return None
        else:
            days_to_search = self.list_log_days()

        # If specific_group is provided, use filter function to navigate directly
        if selector is not None:
            # Convert string to array if needed (backward compatibility)
            specific_group_array = selector

            for day_dir in days_to_search:
                result = self._search_log_file_in_specific_group(
                    day_dir, op_key, specific_group_array
                )
                if result:
                    return result
            return None

        # Search all groups if no specific group provided
        for day_dir in days_to_search:
            result = self._search_log_file_in_groups(
                day_dir.get_root_groups(), op_key, None
            )
            if result:
                return result
        return None

    def _search_log_file_in_specific_group(
        self, day_dir: LogDayDir, op_key_to_find: str, specific_group: list[str]
    ) -> LogFile | None:
        """Search for a log file in a specific group using the filter function."""
        # Build the directory path using the same logic as filter function
        dir_path = day_dir.get_dir_path()
        for i, component in enumerate(specific_group):
            if i % 2 == 1:  # Odd index = dynamic element, needs URL encoding
                dir_path = dir_path / urllib.parse.quote(component, safe="")
            else:  # Even index = structure element, no encoding needed
                dir_path = dir_path / component

        if not dir_path.exists() or not dir_path.is_dir():
            return None

        # Search for function directories in this specific group
        for func_dir_path in dir_path.iterdir():
            if func_dir_path.is_dir():
                # Check if this is a function directory (contains .log files)
                contains_log_files = any(
                    f.suffix == ".log" for f in func_dir_path.iterdir() if f.is_file()
                )
                if contains_log_files:
                    try:
                        # Create LogFuncDir and search for the log file
                        # Need to create the group string that matches what create_log_file creates
                        # Encode dynamic elements (odd indices) to match the stored LogFile.group
                        encoded_group_path = []
                        for i, component in enumerate(specific_group):
                            if (
                                i % 2 == 1
                            ):  # Odd index = dynamic element, needs URL encoding
                                encoded_group_path.append(
                                    urllib.parse.quote(component, safe="")
                                )
                            else:  # Even index = structure element, no encoding needed
                                encoded_group_path.append(component)

                        func_dir = LogFuncDir(
                            date_day=day_dir.date_day,
                            group="/".join(encoded_group_path),
                            func_name=func_dir_path.name,
                            _base_dir=self.base_dir,
                        )
                        # Search through log files in this function directory
                        for log_file in func_dir.get_log_files():
                            if log_file.op_key == op_key_to_find:
                                return log_file
                    except ValueError:
                        # Skip malformed function directories
                        continue

        return None

    def _search_log_file_in_groups(
        self,
        group_dirs: list[LogGroupDir],
        op_key_to_find: str,
        specific_group: str | None = None,
    ) -> LogFile | None:
        """Recursively search for a log file in group directories."""
        for group_dir in group_dirs:
            # Search in function directories of this group
            for func_dir in group_dir.get_log_files():
                # func_dir.get_log_files() returns List[LogFile], sorted newest file first
                for log_file in func_dir.get_log_files():
                    if log_file.op_key == op_key_to_find:
                        return log_file

            # Recursively search in nested groups
            nested_groups = group_dir.get_nested_groups()
            result = self._search_log_file_in_groups(
                nested_groups, op_key_to_find, specific_group
            )
            if result:
                return result

        return None

    def filter(
        self, selector: list[str] | None = None, date_day: str | None = None
    ) -> list[str]:
        """Filter and list folders at the specified hierarchical path.

        Args:
            path: List of path components to navigate to. Empty list returns top-level groups.
                  For alternating structure/dynamic pattern:
                  - ["clans"] lists all dynamic names under clans
                  - ["clans", <name>, "machines"] lists all dynamic names under machines
                  - [] lists all top-level groups
            date_day: Optional date to filter by. If None, uses most recent day.

        Returns:
            List of folder names (decoded) at the specified path level.
        """
        if selector is None:
            selector = []

        # Get the day to search in
        if date_day is None:
            days = self.list_log_days()
            if not days:
                return []
            day_dir = days[0]  # Most recent day
        else:
            if not is_correct_day_format(date_day):
                return []
            try:
                day_dir = LogDayDir(
                    date_day=date_day,
                    _base_dir=self.base_dir,
                    group_configs=self.root_group_configs,
                )
                if not day_dir.get_dir_path().exists():
                    return []
            except ValueError:
                return []

        # Empty path means list top-level groups
        if not selector:
            return list(self.root_group_configs.keys())

        # Build the directory path to search in
        dir_path = day_dir.get_dir_path()
        for i, component in enumerate(selector):
            if i % 2 == 1:  # Odd index = dynamic element, needs URL encoding
                dir_path = dir_path / urllib.parse.quote(component, safe="")
            else:  # Even index = structure element, no encoding needed
                dir_path = dir_path / component

        if not dir_path.exists() or not dir_path.is_dir():
            return []

        # List directories and decode their names
        folder_names = []
        for subdir_path in dir_path.iterdir():
            if subdir_path.is_dir():
                # Decode the directory name
                decoded_name = urllib.parse.unquote(subdir_path.name)
                folder_names.append(decoded_name)

        return sorted(folder_names)
