import ast
import importlib.util
import os
import sys
from dataclasses import is_dataclass
from pathlib import Path

from clan_cli.api.util import type_to_dict
from clan_cli.errors import ClanError


def find_dataclasses_in_directory(
    directory: Path, exclude_paths: list[str] = []
) -> list[tuple[str, str]]:
    """
    Find all dataclass classes in all Python files within a nested directory.

    Args:
        directory (str): The root directory to start searching from.

    Returns:
        List[Tuple[str, str]]: A list of tuples containing the file path and the dataclass name.
    """
    dataclass_files = []

    excludes = [os.path.join(directory, d) for d in exclude_paths]

    for root, _, files in os.walk(directory, topdown=False):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            if file_path in excludes:
                print(f"Skipping dataclass check for file: {file_path}")
                continue

            with open(file_path, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            for deco in node.decorator_list:
                                if (
                                    isinstance(deco, ast.Name)
                                    and deco.id == "dataclass"
                                ):
                                    dataclass_files.append((file_path, node.name))
                                elif (
                                    isinstance(deco, ast.Call)
                                    and isinstance(deco.func, ast.Name)
                                    and deco.func.id == "dataclass"
                                ):
                                    dataclass_files.append((file_path, node.name))
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Error parsing {file_path}: {e}")

    return dataclass_files


def load_dataclass_from_file(
    file_path: str, class_name: str, root_dir: str
) -> type | None:
    """
    Load a dataclass from a given file path.

    Args:
        file_path (str): Path to the file.
        class_name (str): Name of the class to load.

    Returns:
        List[Type]: The dataclass type if found, else an empty list.
    """
    module_name = (
        os.path.relpath(file_path, root_dir).replace(os.path.sep, ".").rstrip(".py")
    )
    # spec = importlib.util.spec_from_file_location(module_name, file_path)
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)
    # breakpoint()
    try:
        sys.path.insert(0, root_dir)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec:
            raise ClanError(f"Could not load spec from file: {file_path}")

        module = importlib.util.module_from_spec(spec)
        if not module:
            raise ClanError(f"Could not create module: {file_path}")

        if not spec.loader:
            raise ClanError(f"Could not load loader from spec: {spec}")

        spec.loader.exec_module(module)

    finally:
        sys.path.pop(0)
    dataclass_type = getattr(module, class_name, None)

    if dataclass_type and is_dataclass(dataclass_type):
        return dataclass_type
    return None


def test_all_dataclasses() -> None:
    # Excludes:
    # - API includes Type Generic wrappers, that are not known in the init file.
    excludes = ["api/__init__.py"]

    cli_path = Path("clan_cli").resolve()
    dataclasses = find_dataclasses_in_directory(cli_path, excludes)

    for file, dataclass in dataclasses:
        print(f"Found dataclass {dataclass} in {file}")
        # The parent directory of the clan_cli is the projects root directory
        try:
            dclass = load_dataclass_from_file(file, dataclass, str(cli_path.parent))
            json_schema = type_to_dict(dclass, scope=f"FILE {file} {dataclass}")
        except Exception as e:
            print(f"Error loading dataclass {dataclass} from {file}: {e}")
            raise ClanError(
                f"Error loading dataclass {dataclass} from {file}: {e}",
                location=__file__,
            )
