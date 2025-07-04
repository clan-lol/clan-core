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
        """Get the display name for this log group.

        Returns:
            The nickname if available, otherwise the group name.
        """
        return self.nickname if self.nickname else self.name

    def add_child(self, child: "LogGroupConfig") -> "LogGroupConfig":
        """Add a child group configuration and return a new LogGroupConfig instance.

        Args:
            child: The child LogGroupConfig to add.

        Returns:
            A new LogGroupConfig instance with the child added.
        """
        new_children = {**self.children, child.name: child}
        return LogGroupConfig(
            name=self.name, nickname=self.nickname, children=new_children
        )

    def get_child(self, name: str) -> "LogGroupConfig | None":
        """Get a child group configuration by name.

        Args:
            name: The name of the child group to retrieve.

        Returns:
            The child LogGroupConfig if found, None otherwise.
        """
        return self.children.get(name)


# Global helper function for format checking (used by LogManager and internally by classes)
def is_correct_day_format(date_day: str) -> bool:
    """Check if the date_day string is in the correct format YYYY-MM-DD.

    Args:
        date_day: The date string to validate.

    Returns:
        True if the date_day matches YYYY-MM-DD format, False otherwise.
    """
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
        """Validate date and time formats after initialization.

        Raises:
            ValueError: If date_day or date_second are not in the correct format.
        """
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
        """Get the datetime object for this log file.

        Returns:
            A datetime object constructed from date_day and date_second.
        """
        # Formats are pre-validated by __post_init__.
        return datetime.datetime.strptime(
            f"{self.date_day} {self.date_second}", "%Y-%m-%d %H-%M-%S"
        ).replace(tzinfo=datetime.UTC)

    def get_file_path(self) -> Path:
        """Get the full file path for this log file.

        Returns:
            The complete Path object for this log file including nested directory structure.
        """
        # Create nested directory structure for hierarchical groups
        path = self._base_dir / self.date_day

        # Split group by slash and create nested directories
        # Dynamic elements are already URL encoded at LogFile creation time
        group_components = self.group.split("/")
        for component in group_components:
            path = path / component

        return path / self.func_name / f"{self.date_second}_{self.op_key}.log"

    def __eq__(self, other: object) -> bool:
        """Check equality with another LogFile instance.

        Args:
            other: The object to compare with.

        Returns:
            True if all significant fields are equal, False otherwise.
        """
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
        """Compare LogFile instances for sorting.

        Sorting order: datetime (newest first), then group, func_name, op_key (all ascending).

        Args:
            other: The object to compare with.

        Returns:
            True if this instance should be sorted before the other.
        """
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
class LogDayDir:
    """Represents a single day's log directory."""

    date_day: str
    _base_dir: Path

    def __post_init__(self) -> None:
        """Validate date format after initialization.

        Raises:
            ValueError: If date_day is not in YYYY-MM-DD format.
        """
        if not is_correct_day_format(self.date_day):
            msg = f"LogDayDir.date_day '{self.date_day}' is not in YYYY-MM-DD format."
            raise ValueError(msg)

    @property
    def _date_obj(self) -> datetime.date:
        """Get the date object for this log day directory.

        Returns:
            A date object constructed from date_day.
        """
        return (
            datetime.datetime.strptime(self.date_day, "%Y-%m-%d")
            .replace(tzinfo=datetime.UTC)
            .date()
        )

    def get_dir_path(self) -> Path:
        """Get the directory path for this log day.

        Returns:
            The Path object for this day's log directory.
        """
        return self._base_dir / self.date_day

    def __eq__(self, other: object) -> bool:
        """Check equality with another LogDayDir instance.

        Args:
            other: The object to compare with.

        Returns:
            True if date_day and base_dir are equal, False otherwise.
        """
        if not isinstance(other, LogDayDir):
            return NotImplemented
        return self.date_day == other.date_day and self._base_dir == other._base_dir

    def __lt__(self, other: object) -> bool:
        """Compare LogDayDir instances for sorting.

        Sorting order: date (newest first).

        Args:
            other: The object to compare with.

        Returns:
            True if this instance should be sorted before the other.
        """
        if not isinstance(other, LogDayDir):
            return NotImplemented
        # Primary sort: date (newest first)
        return self._date_obj > other._date_obj


@dataclass(frozen=True)
class LogManager:
    """Manages hierarchical log files with group configurations and filtering capabilities.

    Provides functionality to create, search, and organize log files in a hierarchical
    directory structure with support for dynamic group names and nicknames.

    Attributes:
        base_dir: The base directory where all log files are stored.
        root_group_configs: Dictionary of root-level group configurations.
    """

    base_dir: Path
    root_group_configs: dict[str, LogGroupConfig] = field(default_factory=dict)

    def add_root_group_config(self, group_config: LogGroupConfig) -> "LogManager":
        """Return a new LogManager with the added root-level group configuration.

        Args:
            group_config: The root-level group configuration to add.

        Returns:
            A new LogManager instance with the group configuration added.
        """
        new_configs = {**self.root_group_configs, group_config.name: group_config}
        return LogManager(base_dir=self.base_dir, root_group_configs=new_configs)

    def find_group_config(self, group_path: list[str]) -> LogGroupConfig | None:
        """Find group configuration by traversing the hierarchical path.

        Only looks at structure elements (even indices), ignoring dynamic names (odd indices).

        Args:
            group_path: The group path components to search for.

        Returns:
            The LogGroupConfig if found, None otherwise.
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

    def create_log_file(
        self, func: Callable, op_key: str, group_path: list[str] | None = None
    ) -> LogFile:
        """Create a new log file for the given function and operation.

        Args:
            func: The function to create a log file for.
            op_key: The operation key identifier.
            group_path: Optional group path components. Defaults to ["default"].

        Returns:
            A new LogFile instance with the log file created on disk.

        Raises:
            ValueError: If the group structure is not registered.
            FileExistsError: If the log file already exists.
        """
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

        Args:
            group_path: The group path components to validate.

        Returns:
            True if the group structure is registered, False otherwise.
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

        Args:
            group_path: The group path components to validate.

        Returns:
            True if the group structure is valid, False otherwise.
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
        """List all available log days in the base directory.

        Returns:
            A sorted list of LogDayDir instances (newest first). Returns empty list if base directory doesn't exist.
        """
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
        op_key: str,
        *,
        date_day: str | None = None,
        selector: list[str] | None = None,
    ) -> LogFile | None:
        """Get a specific log file by operation key.

        Args:
            op_key: The operation key to search for.
            date_day: Optional specific date to search in (YYYY-MM-DD format).
            selector: Optional group path to search in. If None, searches all groups.

        Returns:
            The LogFile if found, None otherwise.
        """
        days_to_search: list[LogDayDir]

        if date_day:
            if not is_correct_day_format(date_day):
                return None
            try:
                target_day_dir = LogDayDir(
                    date_day=date_day,
                    _base_dir=self.base_dir,
                )
                if not target_day_dir.get_dir_path().exists():
                    return None
                days_to_search = [target_day_dir]
            except ValueError:
                return None
        else:
            days_to_search = self.list_log_days()

        # Search for the log file directly using filesystem traversal
        for day_dir in days_to_search:
            result = self._find_log_file_in_day(day_dir, op_key, selector)
            if result:
                return result
        return None

    def _find_log_file_in_day(
        self, day_dir: LogDayDir, op_key: str, selector: list[str] | None = None
    ) -> LogFile | None:
        """Find a log file in a specific day directory.

        Args:
            day_dir: The LogDayDir to search in.
            op_key: The operation key to search for.
            selector: Optional group path to search in. If None, searches all groups.

        Returns:
            The LogFile if found, None otherwise.
        """
        base_path = day_dir.get_dir_path()

        if selector is not None:
            # Search in specific group path
            search_path = base_path
            for i, component in enumerate(selector):
                if i % 2 == 1:  # Odd index = dynamic element, needs URL encoding
                    search_path = search_path / urllib.parse.quote(component, safe="")
                else:  # Even index = structure element, no encoding needed
                    search_path = search_path / component

            if search_path.exists() and search_path.is_dir():
                return self._search_in_path(search_path, op_key, selector)
        else:
            # Search all groups in this day
            if base_path.exists() and base_path.is_dir():
                return self._search_in_path(base_path, op_key, None)

        return None

    def _search_in_path(
        self, search_path: Path, op_key: str, group_path: list[str] | None
    ) -> LogFile | None:
        """Search for log files in a given path.

        Args:
            search_path: The path to search in.
            op_key: The operation key to search for.
            group_path: The group path used to construct the LogFile.

        Returns:
            The LogFile if found, None otherwise.
        """
        log_files: list[LogFile] = []

        # Recursively search for log files
        for log_file_path in search_path.rglob("*.log"):
            if log_file_path.is_file():
                try:
                    # Parse filename to get op_key and time
                    filename_stem = log_file_path.stem
                    parts = filename_stem.split("_", 1)
                    if len(parts) == 2:
                        date_second_str, file_op_key = parts

                        if file_op_key == op_key:
                            # Find the base directory (contains date directories)
                            base_dir = self.base_dir

                            # Get path relative to base directory
                            try:
                                relative_to_base = log_file_path.relative_to(base_dir)
                                path_parts = relative_to_base.parts

                                if len(path_parts) >= 3:  # date/[groups...]/func/file
                                    date_day = path_parts[0]
                                    func_name = path_parts[
                                        -2
                                    ]  # Second to last is function name
                                    group_parts = path_parts[
                                        1:-2
                                    ]  # Between date and function

                                    # Create group string (already URL encoded in filesystem)
                                    group_str = (
                                        "/".join(group_parts)
                                        if group_parts
                                        else "default"
                                    )

                                    if is_correct_day_format(date_day):
                                        log_file = LogFile(
                                            op_key=file_op_key,
                                            date_day=date_day,
                                            group=group_str,
                                            func_name=func_name,
                                            _base_dir=self.base_dir,
                                            date_second=date_second_str,
                                        )
                                        log_files.append(log_file)
                            except ValueError:
                                # Skip files that can't be made relative to base_dir
                                continue
                except (ValueError, IndexError):
                    # Skip malformed files
                    continue

        # Return the newest log file if any found
        if log_files:
            return sorted(log_files)[0]  # LogFile.__lt__ sorts newest first

        return None

    def filter(
        self, selector: list[str] | None = None, date_day: str | None = None
    ) -> list[str]:
        """Filter and list folders at the specified hierarchical path.

        Args:
            selector: List of path components to navigate to. Empty list returns top-level groups.
                     For alternating structure/dynamic pattern:
                     - ["clans"] lists all dynamic names under clans
                     - ["clans", <name>, "machines"] lists all dynamic names under machines
                     - [] lists all top-level groups
            date_day: Optional date to filter by (YYYY-MM-DD format). If None, uses most recent day.

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
