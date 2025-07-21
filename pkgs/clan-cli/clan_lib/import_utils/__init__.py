import contextlib
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar, cast

T = TypeVar("T")


@dataclass(frozen=True)
class ClassSource:
    module_name: str
    file_path: Path
    object_name: str
    line_number: int | None = None

    def vscode_clickable_path(self) -> str:
        """Return a VSCode-clickable path for the class source."""
        return (
            f"{self.module_name}.{self.object_name}: {self.file_path}:{self.line_number}"
            if self.line_number is not None
            else f"{self.module_name}.{self.object_name}: {self.file_path}"
        )

    def __repr__(self) -> str:
        return self.vscode_clickable_path()

    def __str__(self) -> str:
        return self.vscode_clickable_path()


def import_with_source[T](
    module_name: str,
    class_name: str,
    base_class: type[T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Import a class from a module and instantiate it with source information.

    This function dynamically imports a class and adds source location metadata
    that can be used for debugging. The instantiated object will have VSCode-clickable
    paths in its string representation.

    Args:
        module_name: The fully qualified module name to import
        class_name: The name of the class to import from the module
        base_class: The base class type for type checking
        *args: Additional positional arguments to pass to the class constructor
        **kwargs: Additional keyword arguments to pass to the class constructor

    Returns:
        An instance of the imported class with source information

    Example:
        >>> from .network import NetworkTechnologyBase, ClassSource
        >>> tech = import_with_source(
        ...     "clan_lib.network.tor",
        ...     "NetworkTechnology",
        ...     NetworkTechnologyBase
        ... )
        >>> print(tech)  # Outputs: ~/Projects/clan-core/.../tor.py:7
    """
    # Import the module
    module = importlib.import_module(module_name)

    # Get the class from the module
    cls = getattr(module, class_name)

    # Get the line number of the class definition
    line_number = None
    with contextlib.suppress(Exception):
        line_number = inspect.getsourcelines(cls)[1]

    # Get the file path
    file_path_str = module.__file__
    assert file_path_str is not None, f"Module {module_name} file path cannot be None"

    # Make the path relative to home for better readability
    try:
        file_path = Path(file_path_str).relative_to(Path.home())
        file_path = Path("~", file_path)
    except ValueError:
        # If not under home directory, use absolute path
        file_path = Path(file_path_str)

    # Create source information
    source = ClassSource(
        module_name=module_name,
        file_path=file_path,
        object_name=class_name,
        line_number=line_number,
    )

    # Instantiate the class with source information
    return cast(T, cls(source, *args, **kwargs))
