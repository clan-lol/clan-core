import tempfile
from pathlib import Path
from textwrap import dedent
from typing import Any, cast

import pytest

from clan_lib.import_utils import import_with_source
from clan_lib.network.network import NetworkTechnologyBase


def test_import_with_source(tmp_path: Path) -> None:
    """Test importing a class with source information."""
    # Create a temporary module file
    module_dir = tmp_path / "test_module"
    module_dir.mkdir()

    # Create __init__.py to make it a package
    (module_dir / "__init__.py").write_text("")

    # Create a test module with a NetworkTechnology class
    test_module_path = module_dir / "test_tech.py"
    test_module_path.write_text(
        dedent("""
        from clan_lib.network.network import NetworkTechnologyBase

        class NetworkTechnology(NetworkTechnologyBase):
            def __init__(self, source):
                super().__init__(source)
                self.test_value = "test"

            def is_running(self) -> bool:
                return True
    """)
    )

    # Add the temp directory to sys.path
    import sys

    sys.path.insert(0, str(tmp_path))

    try:
        # Import the class using import_with_source
        instance = import_with_source(
            "test_module.test_tech",
            "NetworkTechnology",
            cast(Any, NetworkTechnologyBase),
        )

        # Verify the instance is created correctly
        assert isinstance(instance, NetworkTechnologyBase)
        assert instance.is_running() is True
        assert hasattr(instance, "test_value")
        assert instance.test_value == "test"

        # Verify source information
        assert instance.source.module_name == "test_module.test_tech"
        assert instance.source.file_path.name == "test_tech.py"
        assert instance.source.object_name == "NetworkTechnology"
        assert instance.source.line_number == 4  # Line where class is defined

        # Test string representations
        str_repr = str(instance)
        assert "test_tech.py:" in str_repr
        assert "NetworkTechnology" in str_repr
        assert str(instance.source.line_number) in str_repr

        repr_repr = repr(instance)
        assert "NetworkTechnology" in repr_repr
        assert "test_tech.py:" in repr_repr
        assert "test_module.test_tech.NetworkTechnology" in repr_repr

    finally:
        # Clean up sys.path
        sys.path.remove(str(tmp_path))


def test_import_with_source_with_args() -> None:
    """Test importing a class with additional constructor arguments."""
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            dedent("""
            from clan_lib.network.network import NetworkTechnologyBase

            class NetworkTechnology(NetworkTechnologyBase):
                def __init__(self, source, extra_arg, keyword_arg=None):
                    super().__init__(source)
                    self.extra_arg = extra_arg
                    self.keyword_arg = keyword_arg

                def is_running(self) -> bool:
                    return False
        """)
        )
        temp_file = Path(f.name)

    # Import module dynamically
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("temp_module", temp_file)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["temp_module"] = module
    spec.loader.exec_module(module)

    try:
        # Import with additional arguments
        instance = import_with_source(
            "temp_module",
            "NetworkTechnology",
            cast(Any, NetworkTechnologyBase),
            "extra_value",
            keyword_arg="keyword_value",
        )

        # Verify arguments were passed correctly
        assert instance.extra_arg == "extra_value"  # type: ignore[attr-defined]
        assert instance.keyword_arg == "keyword_value"  # type: ignore[attr-defined]
        assert instance.source.object_name == "NetworkTechnology"

    finally:
        # Clean up
        del sys.modules["temp_module"]
        temp_file.unlink()


def test_import_with_source_module_not_found() -> None:
    """Test error handling when module is not found."""
    with pytest.raises(ModuleNotFoundError):
        import_with_source(
            "non_existent_module", "SomeClass", cast(Any, NetworkTechnologyBase)
        )


def test_import_with_source_class_not_found() -> None:
    """Test error handling when class is not found in module."""
    with pytest.raises(AttributeError):
        import_with_source(
            "clan_lib.network.network",
            "NonExistentClass",
            cast(Any, NetworkTechnologyBase),
        )
