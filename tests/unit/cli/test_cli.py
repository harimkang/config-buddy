import json
from io import StringIO
from pathlib import Path

import pytest
import yaml
from rich.console import Console
from rich.tree import Tree

from configbuddy.cli.cli import CLI


class TestCLI:
    @pytest.fixture
    def sample_config_file(self, tmp_path: Path) -> Path:
        """Create a sample configuration file for testing."""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "admin", "password": "secret"},
            }
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)
        return config_path

    @pytest.fixture
    def console(self, monkeypatch):
        """Create a Console instance for testing."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)

        # Patch the console attribute of CLI class directly
        def mock_cli_init(self, args=None):
            self.console = console
            self.parser = self.init_parser()
            self.add_subcommands()
            self.args = self.parser.parse_args(args)
            self.execute()

        # Patch visualize methods of Config and ConfigDiff
        def mock_visualize(self):
            from configbuddy.core.visualizer import TreeVisualizer

            visualizer = TreeVisualizer()
            tree = visualizer._create_tree(self.source)
            visualizer._build_tree(tree, self.data)
            console.print(tree)

        def mock_diff_visualize(self):
            from configbuddy.core.visualizer import DiffVisualizer

            visualizer = DiffVisualizer()
            tree = Tree("Configuration Differences")  # Create Tree directly
            visualizer._build_diff_sections(tree, self)
            console.print(tree)

        # Patch version command output
        def mock_version_action(self, parser, namespace, values, option_string=None):
            console.print(f"configbuddy {self.version}")
            parser.exit()

        monkeypatch.setattr(CLI, "__init__", mock_cli_init)
        monkeypatch.setattr("configbuddy.core.config.Config.visualize", mock_visualize)
        monkeypatch.setattr("configbuddy.core.types.ConfigDiff.visualize", mock_diff_visualize)
        monkeypatch.setattr("argparse._VersionAction.__call__", mock_version_action)

        return output

    def test_version_command(self, console):
        """Test version command output."""
        with pytest.raises(SystemExit) as exc_info:
            CLI(["-v"])
        assert exc_info.value.code == 0
        output = console.getvalue()
        assert "configbuddy" in output

    def test_visualize_command(self, sample_config_file, console):
        """Test visualize command."""
        CLI(["visualize", str(sample_config_file)])
        output = console.getvalue()

        # Remove ANSI escape sequences
        from re import sub

        output = sub(r"\x1b\[[0-9;]*m", "", output)

        # Check output contains expected elements
        assert "database" in output
        assert "host" in output
        assert "localhost" in output
        assert "credentials" in output

    def test_diff_command(self, tmp_path, console):
        """Test diff command."""
        # Create two config files
        config1 = {"key": "value1"}
        config2 = {"key": "value2"}

        path1 = tmp_path / "config1.yaml"
        path2 = tmp_path / "config2.yaml"

        with open(path1, "w") as f:
            yaml.safe_dump(config1, f)
        with open(path2, "w") as f:
            yaml.safe_dump(config2, f)

        CLI(["diff", str(path1), "--compare", str(path2)])
        output = console.getvalue()

        # Check diff output
        assert "Modified" in output
        assert "value1" in output
        assert "value2" in output

    def test_merge_command(self, tmp_path, console):
        """Test merge command."""
        # Create config files
        config1 = {"a": 1}
        config2 = {"b": 2}
        output_path = tmp_path / "merged.yaml"

        path1 = tmp_path / "config1.yaml"
        path2 = tmp_path / "config2.yaml"

        with open(path1, "w") as f:
            yaml.safe_dump(config1, f)
        with open(path2, "w") as f:
            yaml.safe_dump(config2, f)

        CLI(["merge", str(path1), str(path2), "-o", str(output_path)])

        # Check merged file
        with open(output_path) as f:
            merged = yaml.safe_load(f)
            assert merged["a"] == 1
            assert merged["b"] == 2

    def test_validate_command_valid(self, tmp_path, console):
        """Test validate command with valid config."""
        # Create config and schema
        config = {"name": "test", "age": 25}
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}

        config_path = tmp_path / "config.yaml"
        schema_path = tmp_path / "schema.json"

        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)
        with open(schema_path, "w") as f:
            json.dump(schema, f)

        CLI(["validate", str(config_path), "--schema", str(schema_path)])
        output = console.getvalue()

        assert "valid" in output.lower()

    def test_validate_command_invalid(self, tmp_path, console):
        """Test validate command with invalid config."""
        # Create invalid config
        config = {"name": 123, "age": "invalid"}  # Wrong types
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}

        config_path = tmp_path / "config.yaml"
        schema_path = tmp_path / "schema.json"

        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)
        with open(schema_path, "w") as f:
            json.dump(schema, f)

        CLI(["validate", str(config_path), "--schema", str(schema_path)])
        output = console.getvalue()

        assert "error" in output.lower()

    def test_generate_schema_command(self, tmp_path, console):
        """Test generate-schema command."""
        # Create sample config
        config = {"server": {"host": "localhost", "port": 8080, "debug": True}}

        config_path = tmp_path / "config.yaml"
        schema_path = tmp_path / "schema.json"

        with open(config_path, "w") as f:
            yaml.safe_dump(config, f)

        CLI(["generate-schema", str(config_path), "-o", str(schema_path)])

        # Check generated schema
        with open(schema_path) as f:
            schema = json.load(f)
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "server" in schema["properties"]

    def test_invalid_command(self):
        """Test handling of invalid command."""
        with pytest.raises(SystemExit):
            CLI(["invalid-command"])

    def test_missing_required_args(self):
        """Test handling of missing required arguments."""
        with pytest.raises(SystemExit):
            CLI(["visualize"])  # Missing config path
