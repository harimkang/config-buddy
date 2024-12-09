import pytest

from configbuddy.core.types import ConfigDiff, MergeConflict


class TestConfigDiff:
    @pytest.fixture
    def sample_diff(self) -> ConfigDiff:
        """Create a sample ConfigDiff for testing."""
        return ConfigDiff(
            added={"new_key": "new_value"},
            removed={"old_key": "old_value"},
            modified={"modified_key": ("old_value", "new_value"), "number": (42, 43)},
            unchanged={"stable_key": "stable_value"},
        )

    def test_diff_visualization(self, sample_diff):
        """Test visualization of configuration differences."""
        # Capture visualization output
        import sys
        from io import StringIO

        # Redirect stdout to capture output
        stdout = sys.stdout
        string_io = StringIO()
        sys.stdout = string_io

        try:
            sample_diff.visualize()
            output = string_io.getvalue()

            # Check presence of sections and content
            assert "Added" in output
            assert "Removed" in output
            assert "Modified" in output
            assert "new_key" in output
            assert "old_key" in output
            assert "modified_key" in output
            assert "42" in output
            assert "43" in output
        finally:
            sys.stdout = stdout

    def test_diff_str_representation(self, sample_diff):
        """Test string representation of configuration differences."""
        diff_str = str(sample_diff)

        # Check presence of sections and content
        assert "Added" in diff_str
        assert "Removed" in diff_str
        assert "Modified" in diff_str
        assert "new_key" in diff_str
        assert "old_key" in diff_str
        assert "modified_key" in diff_str
        assert "42" in diff_str
        assert "43" in diff_str

    def test_empty_diff(self):
        """Test visualization of empty configuration differences."""
        empty_diff = ConfigDiff(added={}, removed={}, modified={}, unchanged={})

        diff_str = str(empty_diff)
        assert "Configuration Differences" in diff_str
        assert "Added" not in diff_str
        assert "Removed" not in diff_str
        assert "Modified" not in diff_str


class TestMergeConflict:
    def test_merge_conflict_creation(self):
        """Test creation of MergeConflict instances."""
        conflict = MergeConflict(
            key="test_key",
            values=[1, 2, 3],
            sources=["config1.yaml", "config2.yaml", "config3.yaml"],
        )

        assert conflict.key == "test_key"
        assert conflict.values == [1, 2, 3]
        assert conflict.sources == ["config1.yaml", "config2.yaml", "config3.yaml"]

    def test_merge_conflict_with_different_types(self):
        """Test MergeConflict with different value types."""
        conflict = MergeConflict(
            key="mixed_key",
            values=[42, "string", True],
            sources=["config1.yaml", "config2.yaml", "config3.yaml"],
        )

        assert isinstance(conflict.values[0], int)
        assert isinstance(conflict.values[1], str)
        assert isinstance(conflict.values[2], bool)

    def test_merge_conflict_with_nested_values(self):
        """Test MergeConflict with nested data structures."""
        conflict = MergeConflict(
            key="nested_key",
            values=[{"a": 1}, {"a": 2, "b": 3}, {"c": 4}],
            sources=["config1.yaml", "config2.yaml", "config3.yaml"],
        )

        assert all(isinstance(v, dict) for v in conflict.values)
        assert len(conflict.values) == len(conflict.sources)
