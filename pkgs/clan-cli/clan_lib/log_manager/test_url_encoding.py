# Test file specifically for URL encoding functionality
import urllib.parse
from pathlib import Path

from clan_lib.log_manager import LogGroupConfig, LogManager


def sample_function() -> None:
    """Sample function for testing."""


class TestURLEncoding:
    """Test URL encoding for dynamic group names."""

    def test_dynamic_name_url_encoding_forward_slash(self, tmp_path: Path) -> None:
        """Test that dynamic names with forward slashes get URL encoded."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register structure elements
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Use a dynamic name with forward slashes
        dynamic_name = "/home/user/Projects/qubasas_clan"
        group_path = ["clans", dynamic_name, "default"]

        log_file = log_manager.create_log_file(sample_function, "test_op", group_path)

        # Check that the LogFile uses encoded path for file system operations
        file_path = log_file.get_file_path()
        expected_encoded = urllib.parse.quote(dynamic_name, safe="")

        # Verify the encoded name appears in the file path
        assert expected_encoded in str(file_path)
        assert file_path.exists()

        # Verify that no intermediate directories were created from the forward slashes
        # The encoded name should be a single directory
        day_dir = tmp_path / log_file.date_day / "clans"
        direct_children = [p.name for p in day_dir.iterdir() if p.is_dir()]
        assert len(direct_children) == 1
        assert direct_children[0] == expected_encoded

    def test_dynamic_name_url_encoding_special_characters(self, tmp_path: Path) -> None:
        """Test URL encoding of dynamic names with various special characters."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register structure elements
        clans_config = LogGroupConfig("clans", "Clans")
        machines_config = LogGroupConfig("machines", "Machines")
        clans_config = clans_config.add_child(machines_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Test various special characters
        test_cases = [
            "repo with spaces",
            "repo&with&ampersands",
            "repo!with!exclamations",
            "repo%with%percent",
            "repo@with@symbols",
            "repo#with#hash",
            "repo+with+plus",
        ]

        for dynamic_name in test_cases:
            group_path = ["clans", dynamic_name, "machines", f"machine-{dynamic_name}"]

            log_file = log_manager.create_log_file(
                sample_function,
                f"test_{dynamic_name}",
                group_path,
            )

            # Check that the file was created and encoded names appear in path
            file_path = log_file.get_file_path()
            assert file_path.exists()

            # Verify encoding for both dynamic elements (indices 1 and 3)
            expected_encoded_repo = urllib.parse.quote(dynamic_name, safe="")
            expected_encoded_machine = urllib.parse.quote(
                f"machine-{dynamic_name}",
                safe="",
            )

            assert expected_encoded_repo in str(file_path)
            assert expected_encoded_machine in str(file_path)

    def test_structure_elements_not_encoded(self, tmp_path: Path) -> None:
        """Test that structure elements (even indices) are NOT URL encoded."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register structure elements with special characters in their names
        # (though this is not typical, testing to ensure they're not encoded)
        test_config = LogGroupConfig("test-group", "Test Group")
        sub_config = LogGroupConfig("sub-group", "Sub Group")
        test_config = test_config.add_child(sub_config)
        log_manager = log_manager.add_root_group_config(test_config)

        # Use structure names that contain hyphens (common case)
        group_path = ["test-group", "dynamic-name", "sub-group", "another-dynamic"]

        log_file = log_manager.create_log_file(sample_function, "test_op", group_path)
        file_path = log_file.get_file_path()

        # Structure elements should NOT be encoded
        assert "test-group" in str(file_path)  # Structure element, not encoded
        assert "sub-group" in str(file_path)  # Structure element, not encoded

        # Dynamic elements should be encoded
        expected_dynamic1 = urllib.parse.quote("dynamic-name", safe="")
        expected_dynamic2 = urllib.parse.quote("another-dynamic", safe="")
        assert expected_dynamic1 in str(file_path)
        assert expected_dynamic2 in str(file_path)

    def test_url_encoding_with_unicode_characters(self, tmp_path: Path) -> None:
        """Test URL encoding with Unicode characters in dynamic names."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register structure elements
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Use Unicode characters in dynamic name
        dynamic_name = "项目/中文/测试"  # Chinese characters with slashes
        group_path = ["clans", dynamic_name, "default"]

        log_file = log_manager.create_log_file(
            sample_function,
            "unicode_test",
            group_path,
        )
        file_path = log_file.get_file_path()

        # Check that file was created and Unicode was properly encoded
        assert file_path.exists()
        expected_encoded = urllib.parse.quote(dynamic_name, safe="")
        assert expected_encoded in str(file_path)

        # Verify no intermediate directories from slashes in Unicode string
        day_dir = tmp_path / log_file.date_day / "clans"
        direct_children = [p.name for p in day_dir.iterdir() if p.is_dir()]
        assert len(direct_children) == 1
        assert direct_children[0] == expected_encoded

    def test_backward_compatibility_single_element_paths(self, tmp_path: Path) -> None:
        """Test that single-element paths (no dynamic names) still work."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register simple structure
        default_config = LogGroupConfig("default", "Default")
        log_manager = log_manager.add_root_group_config(default_config)

        # Use simple single-element path (no dynamic names to encode)
        group_path = ["default"]

        log_file = log_manager.create_log_file(
            sample_function,
            "simple_test",
            group_path,
        )
        file_path = log_file.get_file_path()

        # Should work exactly as before
        assert file_path.exists()
        assert "default" in str(file_path)
        # No encoding should have occurred
        assert urllib.parse.quote("default", safe="") == "default"  # No special chars

    def test_empty_dynamic_name_encoding(self, tmp_path: Path) -> None:
        """Test URL encoding with empty string as dynamic name."""
        log_manager = LogManager(base_dir=tmp_path)

        # Register structure elements
        clans_config = LogGroupConfig("clans", "Clans")
        default_config = LogGroupConfig("default", "Default")
        clans_config = clans_config.add_child(default_config)
        log_manager = log_manager.add_root_group_config(clans_config)

        # Use empty string as dynamic name
        group_path = ["clans", "", "default"]

        log_file = log_manager.create_log_file(
            sample_function,
            "empty_test",
            group_path,
        )
        file_path = log_file.get_file_path()

        # Should work - empty string gets encoded as empty string
        assert file_path.exists()
        expected_encoded = urllib.parse.quote("", safe="")
        assert expected_encoded == ""  # Empty string encodes to empty string
