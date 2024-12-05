import pytest
from pathlib import Path
from configbuddy.core.merger import ConfigMerger
from configbuddy.core.config import Config


class TestConfigMerger:
    @pytest.fixture
    def base_config(self) -> Config:
        """Create a base configuration for testing."""
        return Config(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"username": "admin", "password": "secret"},
                },
                "logging": {"level": "INFO", "format": "%(asctime)s - %(message)s"},
            },
            Path("base.yaml"),
        )

    @pytest.fixture
    def override_config(self) -> Config:
        """Create an override configuration for testing."""
        return Config(
            {
                "database": {
                    "host": "127.0.0.1",  # Changed
                    "port": 5432,  # Same
                    "credentials": {
                        "username": "root",  # Changed
                        "password": "new_secret",  # Changed
                    },
                },
                "cache": {  # Added
                    "enabled": True,
                    "ttl": 300,
                },
            },
            Path("override.yaml"),
        )

    def test_merge_empty_configs(self):
        """Test merging with empty config list."""
        with pytest.raises(ValueError, match="No configs to merge"):
            ConfigMerger.merge([])

    def test_merge_single_config(self, base_config):
        """Test merging single configuration."""
        merged, conflicts = ConfigMerger.merge([base_config])
        assert merged.to_dict() == base_config.to_dict()
        assert not conflicts

    def test_deep_merge_two_configs(self, base_config, override_config):
        """Test deep merging of two configurations."""
        merged, conflicts = ConfigMerger.merge(
            [base_config, override_config], strategy="deep"
        )

        # Check merged result
        result = merged.to_dict()
        assert result["database"]["host"] == "127.0.0.1"  # Takes override value
        assert result["database"]["port"] == 5432  # Unchanged value
        assert (
            result["database"]["credentials"]["username"] == "root"
        )  # Takes override value
        assert "cache" in result  # Added section exists
        assert "logging" in result  # Original section remains

        # Check conflicts
        assert len(conflicts) == 3  # host, username, password conflicts
        assert any(c.key == "host" and "127.0.0.1" in c.values for c in conflicts)
        assert any(c.key == "username" and "root" in c.values for c in conflicts)
        assert any(c.key == "password" and "new_secret" in c.values for c in conflicts)

    def test_shallow_merge_two_configs(self, base_config, override_config):
        """Test shallow merging of two configurations."""
        merged, conflicts = ConfigMerger.merge(
            [base_config, override_config], strategy="shallow"
        )

        # Check merged result
        result = merged.to_dict()
        assert (
            result["database"] == override_config.data["database"]
        )  # Takes entire override section
        assert "cache" in result  # Added section exists
        assert "logging" in result  # Original section remains

        # Check conflicts
        assert len(conflicts) == 1  # Only one top-level conflict (database)
        assert conflicts[0].key == "database"

    def test_merge_with_invalid_strategy(self, base_config):
        """Test merging with invalid strategy."""
        with pytest.raises(ValueError, match="Unknown merge strategy"):
            ConfigMerger.merge([base_config], strategy="invalid")

    def test_merge_three_configs(self):
        """Test merging three configurations."""
        config1 = Config({"a": 1, "b": {"x": 1}}, Path("config1.yaml"))
        config2 = Config({"b": {"x": 2, "y": 2}}, Path("config2.yaml"))
        config3 = Config({"b": {"y": 3, "z": 3}}, Path("config3.yaml"))

        merged, conflicts = ConfigMerger.merge(
            [config1, config2, config3], strategy="deep"
        )

        # Check merged result
        result = merged.to_dict()
        assert result["a"] == 1
        assert result["b"]["x"] == 2  # Last value wins
        assert result["b"]["y"] == 3  # Last value wins
        assert result["b"]["z"] == 3

        # Check conflicts
        assert len(conflicts) == 2  # Conflicts for x and y
        assert any(c.key == "x" and c.values == [1, 2] for c in conflicts)
        assert any(c.key == "y" and c.values == [2, 3] for c in conflicts)

    def test_merge_with_none_values(self):
        """Test merging configurations with None values."""
        config1 = Config({"a": None, "b": 1}, Path("config1.yaml"))
        config2 = Config({"a": 2, "b": None}, Path("config2.yaml"))

        merged, conflicts = ConfigMerger.merge([config1, config2], strategy="deep")

        # Check merged result
        result = merged.to_dict()
        assert result["a"] == 2
        assert result["b"] is None

        # Check conflicts
        assert len(conflicts) == 2
        assert any(c.key == "a" and None in c.values for c in conflicts)
        assert any(c.key == "b" and None in c.values for c in conflicts)

    def test_merge_with_list_values(self):
        """Test merging configurations with list values."""
        config1 = Config({"list": [1, 2, 3]}, Path("config1.yaml"))
        config2 = Config({"list": [4, 5, 6]}, Path("config2.yaml"))

        merged, conflicts = ConfigMerger.merge([config1, config2], strategy="deep")

        # Check merged result
        result = merged.to_dict()
        assert result["list"] == [4, 5, 6]  # Last value wins

        # Check conflicts
        assert len(conflicts) == 1
        assert conflicts[0].key == "list"
        assert conflicts[0].values == [[1, 2, 3], [4, 5, 6]]

    def test_merge_conflict_sources(self, base_config, override_config):
        """Test that merge conflicts correctly record their sources."""
        merged, conflicts = ConfigMerger.merge(
            [base_config, override_config], strategy="deep"
        )

        for conflict in conflicts:
            assert len(conflict.sources) == 2
            assert "base.yaml" in conflict.sources[0]
            assert "override.yaml" in conflict.sources[1]

    def test_merge_conflict_details(self):
        """Test detailed merge conflict information."""
        config1 = Config(
            {
                "server": {
                    "host": "localhost",
                    "port": 8080,
                    "settings": {"timeout": 30},
                }
            },
            Path("config1.yaml"),
        )

        config2 = Config(
            {
                "server": {
                    "host": "127.0.0.1",
                    "port": 9000,
                    "settings": {"timeout": 60},
                }
            },
            Path("config2.yaml"),
        )

        _, conflicts = ConfigMerger.merge([config1, config2], strategy="deep")

        # Check number of conflicts
        assert len(conflicts) == 3  # host, port, timeout conflicts

        # Find specific conflicts
        host_conflict = next(c for c in conflicts if c.key == "host")
        port_conflict = next(c for c in conflicts if c.key == "port")
        timeout_conflict = next(c for c in conflicts if c.key == "timeout")

        # Check host conflict
        assert host_conflict.values == ["localhost", "127.0.0.1"]
        assert host_conflict.sources == ["config1.yaml", "config2.yaml"]

        # Check port conflict
        assert port_conflict.values == [8080, 9000]
        assert port_conflict.sources == ["config1.yaml", "config2.yaml"]

        # Check timeout conflict
        assert timeout_conflict.values == [30, 60]
        assert timeout_conflict.sources == ["config1.yaml", "config2.yaml"]

    def test_merge_conflict_with_different_types(self):
        """Test merge conflicts with different value types."""
        config1 = Config(
            {
                "value": 42,  # integer
                "flag": True,  # boolean
                "mixed": "string",  # string
            },
            Path("config1.yaml"),
        )

        config2 = Config(
            {
                "value": "different",  # string (changed to make it actually different)
                "flag": 1,  # integer
                "mixed": False,  # boolean
            },
            Path("config2.yaml"),
        )

        _, conflicts = ConfigMerger.merge([config1, config2], strategy="deep")

        # Check all conflicts
        assert len(conflicts) == 3

        # Check type conflicts
        for conflict in conflicts:
            assert len(conflict.values) == 2
            assert len(conflict.sources) == 2
            assert conflict.sources == ["config1.yaml", "config2.yaml"]

        # Find specific conflicts
        value_conflict = next(c for c in conflicts if c.key == "value")
        flag_conflict = next(c for c in conflicts if c.key == "flag")
        mixed_conflict = next(c for c in conflicts if c.key == "mixed")

        # Check value conflict (int vs str)
        assert value_conflict.values == [42, "different"]

        # Check flag conflict (bool vs int)
        assert flag_conflict.values == [True, 1]

        # Check mixed conflict (str vs bool)
        assert mixed_conflict.values == ["string", False]

    def test_merge_conflict_in_lists(self):
        """Test merge conflicts with list values."""
        config1 = Config(
            {
                "simple_list": [1, 2, 3],
                "nested_list": [
                    {"name": "item1", "value": 10},
                    {"name": "item2", "value": 20},
                ],
            },
            Path("config1.yaml"),
        )

        config2 = Config(
            {
                "simple_list": [4, 5, 6],
                "nested_list": [
                    {"name": "item1", "value": 30},
                    {"name": "item3", "value": 40},
                ],
            },
            Path("config2.yaml"),
        )

        _, conflicts = ConfigMerger.merge([config1, config2], strategy="deep")

        # Find list conflicts
        simple_list_conflict = next(c for c in conflicts if c.key == "simple_list")

        # Check simple list conflict
        assert simple_list_conflict.values == [[1, 2, 3], [4, 5, 6]]
        assert simple_list_conflict.sources == ["config1.yaml", "config2.yaml"]

    def test_merge_conflict_with_none_values(self):
        """Test merge conflicts involving None values."""
        config1 = Config(
            {"nullable": None, "nested": {"value": None}}, Path("config1.yaml")
        )

        config2 = Config(
            {"nullable": "not none", "nested": {"value": 42}}, Path("config2.yaml")
        )

        _, conflicts = ConfigMerger.merge([config1, config2], strategy="deep")

        # Check conflicts involving None
        nullable_conflict = next(c for c in conflicts if c.key == "nullable")
        nested_conflict = next(c for c in conflicts if c.key == "value")

        # Check nullable conflict
        assert nullable_conflict.values == [None, "not none"]
        assert nullable_conflict.sources == ["config1.yaml", "config2.yaml"]

        # Check nested conflict with None
        assert nested_conflict.values == [None, 42]
        assert nested_conflict.sources == ["config1.yaml", "config2.yaml"]
