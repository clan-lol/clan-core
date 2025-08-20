import json
import logging
import os
import re
import shlex
from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import cache
from hashlib import sha1
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from clan_lib.errors import ClanCmdError, ClanError

log = logging.getLogger(__name__)


class FlakeDoesNotExistError(ClanError):
    """Raised when a flake does not exist"""

    def __init__(self, flake_identifier: str, description: str | None = None) -> None:
        msg = f"Flake '{flake_identifier}' does not exist or is not a valid flake."
        super().__init__(msg, description=description, location=flake_identifier)


class FlakeInvalidError(ClanError):
    """Raised when a flake is invalid"""

    def __init__(self, flake_identifier: str, description: str | None = None) -> None:
        msg = f"Flake is invalid. Could not find a flake.nix file in '{flake_identifier}'."
        super().__init__(msg, description=description, location=flake_identifier)


def get_nix_store_dir() -> str:
    """Get the Nix store directory path pattern for regex matching.

    This always returns the pattern that Nix uses in its output,
    which is typically /nix/store regardless of chroot.
    """
    return os.environ.get("NIX_STORE_DIR", "/nix/store")


def get_physical_store_path(store_path: str) -> Path:
    """Convert a store path to its physical location, handling chroot environments.

    When CLAN_TEST_STORE is set, paths like /nix/store/hash-name are
    actually located at CLAN_TEST_STORE/nix/store/hash-name.
    """
    test_store = os.environ.get("CLAN_TEST_STORE")
    if test_store and store_path.startswith("/nix/store/"):
        # Remove leading / to join properly
        relative_path = store_path.lstrip("/")
        return Path(test_store) / relative_path
    return Path(store_path)


@cache
def get_store_path_regex(store_dir: str) -> re.Pattern[str]:
    """Get compiled regex for a specific store directory.

    Matches store paths: store_dir/hash-name
    The hash is base32 lowercase, name can contain [0-9a-zA-Z+-.?=_]
    """
    # Pattern: store_dir/hash-name
    pattern = (
        re.escape(store_dir) + r"/[0-9a-z]+-[0-9a-zA-Z\+\-\._\?=]*"  # hash-name
    )
    return re.compile(pattern)


def find_store_references(text: str) -> list[str]:
    """Find all store path references in a string."""
    store_dir = get_nix_store_dir()
    return get_store_path_regex(store_dir).findall(text)


def is_pure_store_path(path: str) -> bool:
    """Check if a path is a pure Nix store path without file references or metadata.

    Pure store paths have the format: /nix/store/hash-name
    They should NOT contain:
    - Additional path components (/nix/store/hash-name/subdir/file.nix)
    - Line numbers or metadata (/nix/store/hash-name:42)
    """
    store_dir = get_nix_store_dir()
    regex = get_store_path_regex(store_dir)
    return bool(regex.fullmatch(path))


class SetSelectorType(str, Enum):
    """enum for the type of selector in a set.
    For now this is either a string or a maybe selector.
    """

    STR = "str"
    MAYBE = "maybe"


@dataclass
class SetSelector:
    """This class represents a selector used in a set.
    type: SetSelectorType = SetSelectorType.STR
    value: str = ""

    a set looks like this:
    {key1,key2}
    """

    type: SetSelectorType = SetSelectorType.STR
    value: str = ""


class SelectorType(str, Enum):
    """enum for the type of a selector
    this can be all, string, set or maybe
    """

    ALL = "all"
    STR = "str"
    SET = "set"
    MAYBE = "maybe"


@dataclass
class Selector:
    """A class to represent a selector, which selects nix elements one level down.
    consists of a SelectorType and a value.

    if the type is all, no value is needed, since it selects all elements.
    if the type is str, the value is a string, which is the key in a dict.
    if the type is maybe the value is a string, which is the key in a dict.
    if the type is set, the value is a list of SetSelector objects.
    """

    type: SelectorType = SelectorType.STR
    value: str | list[SetSelector] | None = None

    def as_dict(self) -> dict[str, Any]:
        if self.type == SelectorType.SET:
            assert isinstance(self.value, list)
            return {
                "type": self.type.value,
                "value": [asdict(selector) for selector in self.value],
            }
        if self.type == SelectorType.ALL:
            return {"type": self.type.value}
        if self.type == SelectorType.STR:
            assert isinstance(self.value, str)
            return {"type": self.type.value, "value": self.value}
        if self.type == SelectorType.MAYBE:
            assert isinstance(self.value, str)
            return {"type": self.type.value, "value": self.value}
        msg = f"Invalid selector type: {self.type}"
        raise ValueError(msg)


class ClanSelectError(ClanError):
    selectors: list[str]
    failed_attr: str | None = None
    flake_identifier: str

    def __init__(
        self,
        flake_identifier: str,
        selectors: list[str],
        cmd_error: ClanCmdError | None = None,
        description: str | None = None,
    ) -> None:
        attribute = None
        if cmd_error and description is None:
            # Match for "error: <rest of error>"
            error_match = re.search(r"error: (.+)", str(cmd_error))
            if error_match:
                description = error_match.group(1).strip()
        if selectors == []:
            msg = "failed to select []\n"
        elif len(selectors) == 1:
            msg = f"Error on: $ clan select '{selectors[0]}'\n"
        else:
            msg = "Error while executing:"
            for selector in selectors:
                msg += f"$ clan select '{selector}'\n"

        self.selectors = selectors
        self.failed_attr = attribute
        self.flake_identifier = flake_identifier
        super().__init__(msg, description=description, location=flake_identifier)

    def __str__(self) -> str:
        if self.description:
            return f"{self.msg}  Reason: {self.description}"
        return self.msg

    def __repr__(self) -> str:
        return f"ClanSelectError({self})"


def selectors_as_dict(selectors: list[Selector]) -> list[dict[str, Any]]:
    return [selector.as_dict() for selector in selectors]


def selectors_as_json(selectors: list[Selector]) -> str:
    return json.dumps(selectors_as_dict(selectors))


def parse_selector(selector: str) -> list[Selector]:
    """Takes a string and returns a list of selectors.

    a selector can be:
    - a string, which is a key in a dict
    - an integer, which is an index in a list
    - a set of strings or integers, which are keys in a dict or indices in a list.
    - the string "*", which selects all elements in a list or dict
    """
    stack: list[str] = []
    selectors: list[Selector] = []
    acc_str: str = ""

    # only used by set for now
    submode = ""
    acc_selectors: list[SetSelector] = []

    for i in range(len(selector)):
        c = selector[i]
        if stack == []:
            mode = "start"
        else:
            mode = stack[-1]

        if mode == "end":
            if c == ".":
                stack.pop()
                if stack != []:
                    msg = "expected empty stack, but got {stack}"
                    raise ValueError(msg)
            else:
                msg = "expected ., but got {c}"
                raise ValueError(msg)

        elif mode == "start":
            if c == "*":
                stack.append("end")
                selectors.append(Selector(type=SelectorType.ALL))
            elif c == "?":
                stack.append("maybe")
            elif c == '"':
                stack += ["str", "quote"]
            elif c == "{":
                stack.append("set")
            elif c == ".":
                selectors.append(Selector(type=SelectorType.STR, value=acc_str))
            else:
                stack.append("str")
                acc_str += c

        elif mode == "set":
            if submode == "" and c == "?":
                submode = "maybe"
            elif c == "\\":
                stack.append("escape")
                if submode == "":
                    submode = "str"
            elif c == '"':
                stack.append("quote")
                if submode == "":
                    submode = "str"
            elif c == ",":
                if submode == "maybe":
                    set_select_type = SetSelectorType.MAYBE
                else:
                    set_select_type = SetSelectorType.STR
                acc_selectors.append(SetSelector(type=set_select_type, value=acc_str))
                submode = ""
                acc_str = ""
            elif c == "}":
                # Only append selector if we have accumulated content
                if acc_str != "" or submode != "":
                    if submode == "maybe":
                        set_select_type = SetSelectorType.MAYBE
                    else:
                        set_select_type = SetSelectorType.STR
                    acc_selectors.append(
                        SetSelector(type=set_select_type, value=acc_str),
                    )
                # Check for invalid multiselect patterns with outPath
                for subselector in acc_selectors:
                    if subselector.value == "outPath":
                        msg = (
                            "Cannot use 'outPath' in multiselect {...}. "
                            "When nix evaluates attrsets with outPath in a multiselect, "
                            "it collapses the entire attrset to just the outPath string, "
                            "breaking further selection. Use individual selectors instead."
                        )
                        raise ValueError(msg)
                selectors.append(Selector(type=SelectorType.SET, value=acc_selectors))

                submode = ""
                acc_selectors = []

                acc_str = ""
                stack.pop()
                stack.append("end")
            else:
                acc_str += c
                if submode == "":
                    submode = "str"

        elif mode == "quote":
            if c == '"':
                stack.pop()
            elif c == "\\":
                stack.append("escape")
            else:
                acc_str += c

        elif mode == "escape":
            stack.pop()
            acc_str += c

        elif mode in {"str", "maybe"}:
            if c == ".":
                stack.pop()
                if mode == "maybe":
                    select_type = SelectorType.MAYBE
                else:
                    select_type = SelectorType.STR
                selectors.append(Selector(type=select_type, value=acc_str))
                acc_str = ""
            elif c == "\\":
                stack.append("escape")
            else:
                acc_str += c

    if stack != []:
        if stack[-1] == "str" or stack[-1] == "maybe":
            if stack[-1] == "maybe":
                select_type = SelectorType.MAYBE
            else:
                select_type = SelectorType.STR
            selectors.append(Selector(type=select_type, value=acc_str))
        elif stack[-1] == "end":
            pass
        else:
            msg = f"expected empty stack, but got {stack}"
            raise ValueError(msg)

    return selectors


@dataclass
class FlakeCacheEntry:
    """a recursive structure to store the cache.
    consists of a dict with the keys being the selectors and the values being FlakeCacheEntry objects.

    is_list is used to check if the value is a list.
    exists is used to check if the value exists, which can be false if it was selected via maybe.
    fetched_all is used to check if we have all keys on the current level.
    """

    value: str | float | dict[str, Any] | None = field(default_factory=dict)
    is_list: bool = False
    exists: bool = True
    fetched_all: bool = False

    def insert(
        self,
        value: str | float | dict[str, Any] | list[Any] | None,
        selectors: list[Selector],
    ) -> None:
        selector: Selector
        # if we have no more selectors, it means we select all keys from now one and futher down
        if selectors == []:
            selector = Selector(type=SelectorType.ALL)
        else:
            selector = selectors[0]

        # first we find out if we have all subkeys already

        if self.fetched_all:
            pass
        elif selector.type == SelectorType.ALL:
            self.fetched_all = True

        # if we have a string selector, that means we are usually on a dict or a list, since we cannot walk down scalar values
        # so we passthrough the value to the next level
        if selector.type == SelectorType.STR:
            assert isinstance(selector.value, str)
            assert isinstance(self.value, dict)
            if selector.value not in self.value:
                self.value[selector.value] = FlakeCacheEntry()
            self.value[selector.value].insert(value, selectors[1:])

        # if we get a MAYBE, check if the selector is in the output, if not we create a entry with exists = False
        # otherwise we just insert the value into the current dict
        # we can skip creating the non existing entry if we already fetched all keys
        elif selector.type == SelectorType.MAYBE:
            assert isinstance(self.value, dict)
            assert isinstance(value, dict)
            assert isinstance(selector.value, str)
            if selector.value in value:
                if selector.value not in self.value:
                    self.value[selector.value] = FlakeCacheEntry()
                self.value[selector.value].insert(value[selector.value], selectors[1:])
            elif not self.fetched_all:
                if selector.value not in self.value:
                    self.value[selector.value] = FlakeCacheEntry()
                self.value[selector.value].exists = False

        # insert a dict is pretty straight forward
        elif isinstance(value, dict):
            assert isinstance(self.value, dict)
            for key, value_ in value.items():
                if key not in self.value:
                    self.value[key] = FlakeCacheEntry()
                self.value[key].insert(value_, selectors[1:])

        # to store a list we also use a dict, so we know which indices we have
        elif isinstance(value, list):
            self.is_list = True
            fetched_indices: list[str] = []
            # if we are in a set, we take all the selectors
            if selector.type == SelectorType.SET:
                assert isinstance(selector.value, list)
                for subselector in selector.value:
                    fetched_indices.append(subselector.value)
            # if it's just a str, that is the index
            elif selector.type == SelectorType.STR:
                assert isinstance(selector.value, str)
                fetched_indices = [selector.value]
            # otherwise we just take all the indices, which is the length of the list
            elif selector.type == SelectorType.ALL:
                fetched_indices = list(map(str, range(len(value))))

            # insert is the same is insert a dict
            assert isinstance(self.value, dict)
            for i, requested_index in enumerate(fetched_indices):
                assert isinstance(requested_index, str)
                if requested_index not in self.value:
                    self.value[requested_index] = FlakeCacheEntry()
                self.value[requested_index].insert(value[i], selectors[1:])

        # strings need to be checked if they are pure store paths
        # if they are, we store them as a dict with the outPath key
        # this is to mirror nix behavior, where the outPath of an attrset is used if no further key is specified
        elif isinstance(value, str) and is_pure_store_path(value):
            assert selectors == []
            self.value = {"outPath": FlakeCacheEntry(value)}

        # if we have a normal scalar, we check if it conflicts with a maybe already store value
        # since an empty attrset is the default value, we cannot check that, so we just set it to the value
        elif isinstance(value, float | int | str) or value is None:
            assert selectors == []
            if self.value == {}:
                self.value = value
            # Only check for outPath wrapping conflicts for strings (store paths)
            elif isinstance(value, str) and (
                isinstance(self.value, dict)
                and "outPath" in self.value
                and isinstance(self.value["outPath"], FlakeCacheEntry)
            ):
                # If the same value is already wrapped in outPath, it's not a conflict
                if self.value["outPath"].value == value:
                    # Value already cached as outPath, no need to change
                    pass
                else:
                    msg = f"Cannot insert {value} into cache, already have {self.value}"
                    raise TypeError(msg)
            elif self.value != value:
                msg = f"Cannot insert {value} into cache, already have {self.value}"
                raise TypeError(msg)

    def is_cached(self, selectors: list[Selector]) -> bool:
        selector: Selector

        # for store paths we have to check if they still exist, otherwise they have to be rebuild and are thus not cached
        if isinstance(self.value, str):
            store_refs = find_store_references(self.value)
            if store_refs:
                # Check if all store references exist at their physical location
                return all(get_physical_store_path(ref).exists() for ref in store_refs)

        # if self.value is not dict but we request more selectors, we assume we are cached and an error will be thrown in the select function
        if isinstance(self.value, str | float | int | None):
            return True

        if selectors == []:
            selector = Selector(type=SelectorType.ALL)
        else:
            selector = selectors[0]

        # we just fetch all subkeys, so we need to check of we inserted all keys at this level before
        if selector.type == SelectorType.ALL:
            assert isinstance(self.value, dict)
            if self.fetched_all:
                result = all(
                    self.value[sel].is_cached(selectors[1:]) for sel in self.value
                )
                return result
            return False
        if (
            selector.type == SelectorType.SET
            and isinstance(selector.value, list)
            and isinstance(self.value, dict)
        ):
            for requested_selector in selector.value:
                val = requested_selector.value
                if val not in self.value:
                    # if we fetched all keys and we are not in the dict, we can assume we are cached
                    return self.fetched_all
                # if a key does not exist from a previous fetch, we can assume it is cached
                if self.value[val].exists is False:
                    return True
                if not self.value[val].is_cached(selectors[1:]):
                    return False

            return True

        # string and maybe work the same for cache checking
        if (selector.type in (SelectorType.STR, SelectorType.MAYBE)) and isinstance(
            self.value, dict
        ):
            assert isinstance(selector.value, str)
            val = selector.value
            if val not in self.value:
                # if we fetched all keys and we are not in there, refetching won't help, so we can assume we are cached
                return self.fetched_all
            if self.value[val].exists is False:
                return True
            return self.value[val].is_cached(selectors[1:])

        return False

    def select(self, selectors: list[Selector]) -> Any:
        selector: Selector
        if selectors == []:
            selector = Selector(type=SelectorType.ALL)
        else:
            selector = selectors[0]

        # mirror nix behavior where we return outPath if no further selector is specified
        if selectors == [] and isinstance(self.value, dict) and "outPath" in self.value:
            return self.value["outPath"].value

        # if we are at the end of the selector chain, we return the value
        if selectors == [] and isinstance(self.value, str | float | int | None):
            return self.value

        # if we fetch a specific key, we return the recurse into that value in the dict
        if selector.type == SelectorType.STR and isinstance(self.value, dict):
            assert isinstance(selector.value, str)
            return self.value[selector.value].select(selectors[1:])

        # if we are a MAYBE selector, we check if the key exists in the dict
        if selector.type == SelectorType.MAYBE:
            assert isinstance(selector.value, str)
            if isinstance(self.value, dict):
                if selector.value in self.value:
                    if self.value[selector.value].exists:
                        return {
                            selector.value: self.value[selector.value].select(
                                selectors[1:],
                            ),
                        }
                    return {}
                # Key not found, return empty dict for MAYBE selector
                return {}
            # Non-dict value (including None), return empty dict for MAYBE selector
            return {}

        # Handle SET selector on non-dict values
        if selector.type == SelectorType.SET and not isinstance(self.value, dict):
            assert isinstance(selector.value, list)
            # Empty set or all sub-selectors are MAYBE
            if len(selector.value) == 0:
                # Empty set, return empty dict
                return {}
            all_maybe = all(
                subselector.type == SetSelectorType.MAYBE
                for subselector in selector.value
            )
            if all_maybe:
                # All sub-selectors are MAYBE, return empty dict for non-dict values
                return {}
            # Not all sub-selectors are MAYBE, fall through to raise KeyError

        # otherwise we return a list or a dict
        if isinstance(self.value, dict):
            keys_to_select: list[str] = []
            # if we want to select all keys, we take all existing sub elements
            if selector.type == SelectorType.ALL:
                for key in self.value:
                    if self.value[key].exists:
                        keys_to_select.append(key)

            # if we want to select a set of keys, we take the keys from the selector
            if selector.type == SelectorType.SET:
                assert isinstance(selector.value, list)
                for subselector in selector.value:
                    # make sure the keys actually exist if we have a maybe selector
                    if subselector.type == SetSelectorType.MAYBE:
                        if (
                            subselector.value in self.value
                            and self.value[subselector.value].exists
                        ):
                            keys_to_select.append(subselector.value)
                    else:
                        keys_to_select.append(subselector.value)

            # if we are a list, return a list
            if self.is_list:
                result_list: list[Any] = []
                for index in keys_to_select:
                    result_list.append(self.value[index].select(selectors[1:]))
                return result_list

            # otherwise return a dict
            result_dict: dict[str, Any] = {}
            for key in keys_to_select:
                value = self.value[key].select(selectors[1:])
                if self.value[key].exists:
                    # Skip empty dicts when the original value is None
                    if not (
                        isinstance(value, dict)
                        and len(value) == 0
                        and self.value[key].value is None
                    ):
                        result_dict[key] = value
            return result_dict

        # return a KeyError if we cannot fetch the key
        str_selector: str
        if selector.type == SelectorType.ALL:
            str_selector = "*"
        elif selector.type == SelectorType.SET:
            subselectors: list[str] = []
            assert isinstance(selector.value, list)
            for subselector in selector.value:
                subselectors.append(subselector.value)
            str_selector = "{" + ",".join(subselectors) + "}"
        else:
            assert isinstance(selector.value, str)
            str_selector = selector.value

        raise KeyError(str_selector)

    def __getitem__(self, name: str) -> "FlakeCacheEntry":
        if isinstance(self.value, dict):
            return self.value[name]
        raise KeyError(name)

    def as_json(self) -> dict[str, Any]:
        json_data: Any = {}
        if isinstance(self.value, dict):
            value = json_data["value"] = {}
            for k, v in self.value.items():
                value[k] = v.as_json()
        else:  # == str | float | None
            json_data["value"] = self.value

        json_data["is_list"] = self.is_list
        json_data["exists"] = self.exists
        json_data["fetched_all"] = self.fetched_all
        return json_data

    @staticmethod
    def from_json(json_data: dict[str, Any]) -> "FlakeCacheEntry":
        raw_value = json_data.get("value")
        if isinstance(raw_value, dict):
            value: Any = {}
            for k, v in raw_value.items():
                value[k] = FlakeCacheEntry.from_json(v)
        else:  # == str | float | None
            value = raw_value

        is_list = json_data.get("is_list", False)
        exists = json_data.get("exists", True)
        fetched_all = json_data.get("fetched_all", False)

        entry = FlakeCacheEntry(
            value=value,
            is_list=is_list,
            exists=exists,
            fetched_all=fetched_all,
        )
        return entry

    def __repr__(self) -> str:
        if isinstance(self.value, dict):
            return f"FlakeCache {{{', '.join([str(k) for k in self.value])}}}"
        return f"FlakeCache {self.value}"


@dataclass
class FlakeCache:
    """an in-memory cache for flake outputs, uses a recursive FLakeCacheEntry structure"""

    def __init__(self) -> None:
        self.cache: FlakeCacheEntry = FlakeCacheEntry()

    def insert(self, data: dict[str, Any], selector_str: str) -> None:
        if selector_str:
            selectors = parse_selector(selector_str)
        else:
            selectors = []

        self.cache.insert(data, selectors)

    def select(self, selector_str: str) -> Any:
        selectors = parse_selector(selector_str)
        return self.cache.select(selectors)

    def is_cached(self, selector_str: str) -> bool:
        selectors = parse_selector(selector_str)
        return self.cache.is_cached(selectors)

    def save_to_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as temp_file:
            data = {"cache": self.cache.as_json()}
            json.dump(data, temp_file)
            temp_file.close()
            Path(temp_file.name).rename(path)

    def load_from_file(self, path: Path) -> None:
        with path.open("r") as f:
            log.debug(f"Loading flake cache from file {path}")
            data = json.load(f)
            self.cache = FlakeCacheEntry.from_json(data["cache"])


@dataclass
class Flake:
    """This class represents a flake, and is used to interact with it.
    values can be accessed using the select method, which will fetch the value from the cache if it is present.
    """

    identifier: str
    hash: str | None = None
    store_path: str | None = None
    nix_options: list[str] | None = None

    _flake_cache_path: Path | None = field(init=False, default=None)
    _cache: FlakeCache | None = field(init=False, default=None)
    _path: Path | None = field(init=False, default=None)
    _is_local: bool | None = field(init=False, default=None)

    @classmethod
    def from_json(
        cls: type["Flake"],
        data: dict[str, Any],
        *,
        nix_options: list[str] | None = None,
    ) -> "Flake":
        return cls(data["identifier"], nix_options=nix_options)

    def __str__(self) -> str:
        return self.identifier

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Flake):
            return NotImplemented
        return self.identifier == other.identifier

    @property
    def is_local(self) -> bool:
        if self._is_local is None:
            self.invalidate_cache()
        assert isinstance(self._is_local, bool)
        return self._is_local

    def get_input_names(self) -> list[str]:
        log.debug("flake.get_input_names is deprecated and will be removed")
        flakes = self.select("inputs.*._type")
        return list(flakes.keys())

    @property
    def path(self) -> Path:
        if self._path is None:
            self.invalidate_cache()
        assert isinstance(self._path, Path)
        return self._path

    def load_cache(self) -> None:
        path = self.flake_cache_path
        if path is None or self._cache is None or not path.exists():
            return
        try:
            self._cache.load_from_file(path)
        except Exception as e:
            log.warning(f"Failed load eval cache: {e}. Continue without cache")

    def prefetch(self) -> None:
        """Loads the flake into the store and populates self.store_path and self.hash such that the flake can evaluate locally and offline"""
        from clan_lib.cmd import RunOpts, run
        from clan_lib.nix import (
            nix_command,
        )

        if self.nix_options is None:
            self.nix_options = []

        cmd = [
            "flake",
            "prefetch",
            "--json",
            *self.nix_options,
            "--option",
            "flake-registry",
            "",
            self.identifier,
        ]

        trace_prefetch = os.environ.get("CLAN_DEBUG_NIX_PREFETCH", False) == "1"
        if not trace_prefetch:
            log.debug(f"Prefetching flake {self.identifier}")
        try:
            flake_prefetch = run(nix_command(cmd), RunOpts(trace=trace_prefetch))
        except ClanCmdError as e:
            if (
                f"error: getting status of '{self.identifier}': No such file or directory"
                in str(e)
            ):
                raise FlakeDoesNotExistError(self.identifier) from e
            if "error: could not find a flake.nix file":
                raise FlakeInvalidError(self.identifier) from e
            raise

        flake_metadata = json.loads(flake_prefetch.stdout)
        self.store_path = flake_metadata["storePath"]
        self.hash = flake_metadata["hash"]
        self.flake_metadata = flake_metadata

    def invalidate_cache(self) -> None:
        """Invalidate the cache and reload it.

        This method is used to refresh the cache by reloading it from the flake.
        """
        from clan_lib.dirs import user_cache_dir
        from clan_lib.nix import (
            nix_metadata,
        )

        self.prefetch()

        self._cache = FlakeCache()
        assert self.hash is not None
        hashed_hash = sha1(self.hash.encode()).hexdigest()
        self.flake_cache_path = (
            Path(user_cache_dir()) / "clan" / "flakes-v2" / hashed_hash
        )
        self.load_cache()

        if "original" not in self.flake_metadata:
            self.flake_metadata = nix_metadata(self.identifier)

        if self.flake_metadata["original"].get("url", "").startswith("file:"):
            self._is_local = True
            path = self.flake_metadata["original"]["url"].removeprefix("file://")
            path = path.removeprefix("file:")
            self._path = Path(path)
        elif self.flake_metadata["original"].get("path"):
            self._is_local = True
            self._path = Path(self.flake_metadata["original"]["path"])
        else:
            self._is_local = False
            assert self.store_path is not None
            self._path = Path(self.store_path)

    def get_from_nix(
        self,
        selectors: list[str],
    ) -> None:
        """Retrieves specific attributes from a Nix flake using the provided selectors.

        This function interacts with the Nix build system to fetch and process
        attributes from a flake. It uses the provided selectors to determine which
        attributes to retrieve and optionally accepts additional Nix options for
        customization. The results are cached for future use.
        Used mostly as a lowlevel function for `precache` and `select` methods.

        Args:
            selectors (list[str]): A list of attribute selectors to fetch from the flake.
            nix_options (list[str] | None): Optional additional options to pass to the Nix build command.

        Raises:
            ClanError: If the number of outputs does not match the number of selectors.
            AssertionError: If the cache or flake cache path is not properly initialized.

        """
        from clan_lib.cmd import Log, RunOpts, run
        from clan_lib.dirs import select_source
        from clan_lib.nix import (
            nix_build,
            nix_config,
            nix_test_store,
        )

        if self._cache is None:
            self.invalidate_cache()
        assert self._cache is not None

        nix_options = self.nix_options[:] if self.nix_options is not None else []

        str_selectors: list[str] = []
        for selector in selectors:
            str_selectors.append(selectors_as_json(parse_selector(selector)))

        config = nix_config()

        select_hash = "@select_hash@"
        if not select_hash.startswith("sha256-"):
            select_flake = Flake(str(select_source()), nix_options=nix_options)
            select_flake.invalidate_cache()
            assert select_flake.hash is not None, (
                "this should be impossible as invalidate_cache() should always set `hash`"
            )
            select_hash = select_flake.hash

        # fmt: off
        nix_code = f"""
            let
              flake = builtins.getFlake "path:{self.store_path}?narHash={self.hash}";
              selectLib = (
                builtins.getFlake
                  "path:{select_source()}?narHash={select_hash}"
              ).lib;
            in
              derivation {{
                name = "clan-flake-select";
                result = builtins.toJSON [
                    {" ".join(
                        [
                            f"(selectLib.applySelectors (builtins.fromJSON ''{attr}'') flake)"
                            for attr in str_selectors
                        ]
                    )}
                ];

                # We can always build this derivation locally, since /bin/sh is system independent,
                # remote builders would introduce needless overhead.
                preferLocalBuild = true;
                # Save the roundtrip to check the binary caches for trival substitutions
                allowSubstitutes = false;

                passAsFile = [ "result" ];
                system = "{config["system"]}";
                builder = "/bin/sh";
                args = [
                  "-c"
                  ''
                     read -r x < "$resultPath"; printf %s "$x" > $out
                  ''
                ];
              }}
        """
        trace = os.environ.get("CLAN_DEBUG_NIX_SELECTORS", False) == "1"
        try:
            build_output = Path(
                run(
                    nix_build(["--expr", nix_code, *nix_options]),
                    RunOpts(log=Log.NONE, trace=trace),
                ).stdout.strip(),
            )
        except ClanCmdError as e:
            if "error: attribute 'clan' missing" in str(e):
                msg = ("This flake does not export the 'clan' attribute. \n"
                    "Please write 'clan = clan.config;' into the outputs of your flake.nix.")
                raise ClanSelectError(
                    flake_identifier=self.identifier,
                    selectors=selectors,
                    cmd_error=e,
                    description=msg,
                ) from e

            # If the error is about a missing attribute, we raise a ClanSelectError
            # with the failed selectors and the flake identifier.
            raise ClanSelectError(
                flake_identifier=self.identifier,
                selectors=selectors,
                cmd_error=e,
            ) from e



        if tmp_store := nix_test_store():
            build_output = tmp_store.joinpath(*build_output.parts[1:])
        outputs = json.loads(build_output.read_bytes())
        if len(outputs) != len(selectors):
            msg = f"flake_prepare_cache: Expected {len(outputs)} outputs, got {len(selectors)}"
            raise ClanError(msg)
        self.load_cache()
        for i, selector in enumerate(selectors):
            self._cache.insert(outputs[i], selector)
        if self.flake_cache_path:
            self._cache.save_to_file(self.flake_cache_path)

    def precache(self, selectors: list[str]) -> None:
        """Ensures that the specified selectors are cached locally.

        This function checks if the given selectors are already cached. If not, it
        fetches them using the Nix build system and stores them in the local cache.
        It ensures that the cache is initialized before performing these operations.

        Args:
            selectors (list[str]): A list of attribute selectors to check and cache.

        """
        if self._cache is None:
            self.invalidate_cache()
        assert self._cache is not None
        assert self.flake_cache_path is not None
        not_fetched_selectors = []
        for selector in selectors:
            if not self._cache.is_cached(selector):
                not_fetched_selectors.append(selector)

        if not_fetched_selectors:
            self.get_from_nix(not_fetched_selectors)

    def select(
        self,
        selector: str,
    ) -> Any:
        """Selects a value from the cache based on the provided selector string.
        Fetches it via nix_build if it is not already cached.

        Args:
            selector (str): The attribute selector string to fetch the value for.

        """
        if self._cache is None:
            self.invalidate_cache()
        assert self._cache is not None
        assert self.flake_cache_path is not None

        if not self._cache.is_cached(selector):
            log.debug(f"(cached) $ clan select {shlex.quote(selector)}")
            log.debug(f"Cache miss for {selector}")
            self.get_from_nix([selector])
        else:
            log.debug(f"$ clan select {shlex.quote(selector)}")

        value = self._cache.select(selector)
        return value

    def select_machine(self, machine_name: str, selector: str) -> Any:
        """Select a nix attribute for a specific machine.

        Args:
            machine_name: The name of the machine
            selector: The attribute selector string relative to the machine config
            apply: Optional function to apply to the result

        """
        from clan_lib.nix import nix_config

        config = nix_config()
        system = config["system"]

        full_selector = f'clanInternals.machines."{system}"."{machine_name}".{selector}'
        return self.select(full_selector)


def require_flake(flake: Flake | None) -> Flake:
    """Require that a flake argument is provided, if not in a clan flake.

    This should be called by commands that require a flake but don't have
    a sensible default when no clan flake is found locally.

    Args:
        flake: The flake object to check, may be None

    Returns:
        The validated flake object

    Raises:
        ClanError: If the flake is None

    """
    if flake is None:
        msg = "No clan flake found in the current directory or its parents"
        raise ClanError(
            msg,
            description="Use the --flake flag to specify a clan flake path or URL",
        )
    return flake
