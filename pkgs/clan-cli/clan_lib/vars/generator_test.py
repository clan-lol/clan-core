from .generator import filter_machine_specific_attrs


def test_filter_machine_specific_attrs_removes_platform_attrs() -> None:
    """Test that owner, group, and mode are filtered out."""
    files = {
        "key": {
            "secret": True,
            "deploy": True,
            "owner": "root",
            "group": "wheel",
            "mode": "0400",
            "neededFor": "services",
        }
    }
    result = filter_machine_specific_attrs(files)
    expected = {
        "key": {
            "secret": True,
            "deploy": True,
            "neededFor": "services",
        }
    }
    assert result == expected


def test_filter_machine_specific_attrs_preserves_other_attrs() -> None:
    """Test that non-platform-specific attributes are preserved."""
    files = {
        "file1": {
            "secret": False,
            "deploy": True,
            "neededFor": "boot",
        },
        "file2": {
            "secret": True,
            "deploy": False,
            "neededFor": "services",
        },
    }
    result = filter_machine_specific_attrs(files)
    assert result == files


def test_filter_machine_specific_attrs_multiple_files() -> None:
    """Test filtering across multiple files."""
    files = {
        "key": {
            "secret": True,
            "owner": "root",
            "group": "root",
            "mode": "0400",
        },
        "key.pub": {
            "secret": False,
            "owner": "root",
            "group": "wheel",
            "mode": "0444",
        },
    }
    result = filter_machine_specific_attrs(files)
    expected = {
        "key": {"secret": True},
        "key.pub": {"secret": False},
    }
    assert result == expected


def test_filter_machine_specific_attrs_empty_dict() -> None:
    """Test that empty dict returns empty dict."""
    result = filter_machine_specific_attrs({})
    assert result == {}


def test_filter_machine_specific_attrs_no_machine_attrs() -> None:
    """Test files with no machine-specific attributes."""
    files = {
        "config": {
            "secret": False,
            "deploy": True,
        }
    }
    result = filter_machine_specific_attrs(files)
    assert result == files
