from dataclasses import dataclass
from pathlib import Path

import pytest

from configbuddy.core.types import ConfigDiff
from configbuddy.core.visualizer import DiffVisualizer, TreeVisualizer


@dataclass
class MockConfig:
    """Mock implementation of ConfigData protocol for testing."""

    _data: dict
    _source: Path | None = None

    @property
    def data(self) -> dict:
        return self._data

    @property
    def source(self) -> Path | None:
        return self._source


class TestTreeVisualizer:
    @pytest.fixture
    def sample_config(self) -> MockConfig:
        """Create a sample configuration for testing."""
        return MockConfig(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"username": "admin", "password": "secret"},
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(message)s",
                    "enabled": True,
                    "handlers": ["console", "file"],
                },
            },
            Path("config.yaml"),
        )

    def test_tree_visualization_structure(self, sample_config):
        """Test that tree visualization contains all config elements."""
        visualizer = TreeVisualizer()
        result = visualizer.to_string(sample_config)

        # Check presence of all keys
        assert "database" in result
        assert "host" in result
        assert "port" in result
        assert "credentials" in result
        assert "logging" in result
        assert "level" in result

        # Check values are properly formatted
        assert "localhost" in result
        assert "5432" in result
        assert "INFO" in result
        assert "true" in result.lower()  # boolean formatting
        assert "console" in result
        assert "file" in result

    def test_tree_root_display(self):
        """Test root node display with and without source."""
        config_no_source = MockConfig({"key": "value"})
        config_with_source = MockConfig({"key": "value"}, Path("test.yaml"))

        visualizer = TreeVisualizer()
        result_no_source = visualizer.to_string(config_no_source)
        result_with_source = visualizer.to_string(config_with_source)

        assert "Config" in result_no_source
        assert "test.yaml" in result_with_source

    def test_tree_format_values(self):
        """Test formatting of different value types."""
        config = MockConfig(
            {
                "numbers": {
                    "integer": 42,
                    "float": 3.14,
                },
                "strings": {
                    "simple": "hello",
                    "empty": "",
                },
                "booleans": {
                    "true": True,
                    "false": False,
                },
                "special": {
                    "none": None,
                    "custom": object(),  # 기타 타입 테스트
                },
            }
        )

        visualizer = TreeVisualizer()
        result = visualizer.to_string(config)

        # Check number formatting
        assert "42" in result  # integer
        assert "3.14" in result  # float

        # Check string formatting
        assert '"hello"' in result  # 따옴표로 둘러싸인 문자열
        assert '""' in result  # 빈 문자열

        # Check boolean formatting
        assert "true" in result.lower()  # 소문자 boolean
        assert "false" in result.lower()

        # Check special values
        assert "null" in result.lower()  # None 값
        assert "object" in result.lower()  # 기타 타입

    def test_tree_visualize_to_console(self, sample_config):
        """Test visualization to console output."""
        import sys
        from io import StringIO

        # Redirect stdout to capture output
        stdout = sys.stdout
        string_io = StringIO()
        sys.stdout = string_io

        try:
            visualizer = TreeVisualizer()
            visualizer.visualize(sample_config)
            output = string_io.getvalue()

            # Check structure in console output
            assert "database" in output
            assert "host" in output
            assert "port" in output
            assert "localhost" in output
            assert "5432" in output
        finally:
            sys.stdout = stdout

    def test_tree_nested_lists(self):
        """Test visualization of nested lists."""
        config = MockConfig(
            {
                "simple_list": [1, 2, 3],
                "nested_list": [
                    {"name": "item1", "value": 10},
                    {"name": "item2", "value": 20},
                ],
                "mixed_list": [42, "string", {"key": "value"}, [1, 2, 3]],
            }
        )

        visualizer = TreeVisualizer()
        result = visualizer.to_string(config)

        # Check list indices and values
        assert "[0]" in result
        assert "[1]" in result
        assert "item1" in result
        assert "item2" in result
        assert "42" in result
        assert '"string"' in result
        assert "value" in result


class TestDiffVisualizer:
    @pytest.fixture
    def sample_diff(self) -> ConfigDiff:
        """Create a sample configuration diff for testing."""
        return ConfigDiff(
            added={"new_key": "new_value"},
            removed={"old_key": "old_value"},
            modified={"modified_key": ("old_value", "new_value"), "number": (42, 43)},
            unchanged={"stable_key": "stable_value"},
        )

    def test_diff_visualization_structure(self, sample_diff):
        """Test that diff visualization shows all sections properly."""
        visualizer = DiffVisualizer()
        result = visualizer.to_string(sample_diff)

        # Check section headers
        assert "Added" in result
        assert "Removed" in result
        assert "Modified" in result

        # Check content
        assert "new_key" in result
        assert "old_key" in result
        assert "modified_key" in result
        assert "old_value" in result
        assert "new_value" in result

    def test_empty_diff_sections(self):
        """Test visualization of diff with empty sections."""
        empty_diff = ConfigDiff(added={}, removed={}, modified={}, unchanged={"key": "value"})

        visualizer = DiffVisualizer()
        result = visualizer.to_string(empty_diff)

        # Empty diff should still create valid output
        assert "Configuration Differences" in result
        # But should not include empty sections
        assert "Added" not in result
        assert "Removed" not in result
        assert "Modified" not in result

    def test_nested_diff_visualization(self):
        """Test visualization of nested differences."""
        nested_diff = ConfigDiff(
            added={"parent": {"child": "value"}},
            removed={"old_parent": {"old_child": "value"}},
            modified={"nested": ({"old_key": "old_value"}, {"new_key": "new_value"})},
            unchanged={},
        )

        visualizer = DiffVisualizer()
        result = visualizer.to_string(nested_diff)

        # Check nested structure
        assert "parent" in result
        assert "child" in result
        assert "old_parent" in result
        assert "old_child" in result
        assert "nested" in result
        assert "old_key" in result
        assert "new_key" in result

    def test_diff_tree_with_nested_structures(self):
        """Test building diff tree with nested structures."""
        diff = ConfigDiff(
            added={
                "level1": {"level2": {"level3": "value"}},
                "list": [1, 2, {"key": "value"}],
            },
            removed={"old_nested": {"sub": {"data": 42}}},
            modified={"nested": ({"old": {"value": 1}}, {"new": {"value": 2}})},
            unchanged={},
        )

        visualizer = DiffVisualizer()
        result = visualizer.to_string(diff)

        # Check nested structure in added section
        assert "level1" in result
        assert "level2" in result
        assert "level3" in result
        assert "value" in result

        # Check list handling in added section
        assert "[0]" in result
        assert "[1]" in result
        assert "[2]" in result

        # Check nested structure in removed section
        assert "old_nested" in result
        assert "sub" in result
        assert "data" in result
        assert "42" in result

        # Check modified section with nested structures
        assert "old" in result
        assert "new" in result
        assert "1" in result
        assert "2" in result

    def test_diff_tree_with_various_value_types(self):
        """Test diff tree with various value types."""
        diff = ConfigDiff(
            added={
                "number": 42,
                "float": 3.14,
                "string": "hello",
                "boolean": True,
                "none": None,
                "list": [1, "two", False],
            },
            removed={},
            modified={
                "mixed": (42, "string"),
                "bools": (True, False),
                "numbers": (1, 2.5),
            },
            unchanged={},
        )

        visualizer = DiffVisualizer()
        result = visualizer.to_string(diff)

        # Check added section with different types
        assert "42" in result
        assert "3.14" in result
        assert "hello" in result
        assert "true" in result.lower()
        assert "null" in result.lower()
        assert "[1]" in result
        assert "two" in result
        assert "false" in result.lower()

        # Check modified section with type changes
        assert "42" in result
        assert "string" in result
        assert "true" in result.lower()
        assert "false" in result.lower()
        assert "2.5" in result
