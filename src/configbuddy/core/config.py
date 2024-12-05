# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any
import yaml
import json
import configparser
from .visualizer import TreeVisualizer
from .types import ConfigDiff, MergeConflict


class Config:
    """Base class for representing configuration file contents.

    This class provides functionality to load, save, and visualize configuration data
    from various file formats including YAML, JSON, and INI.
    """

    def __init__(self, data: dict[str, Any], source: Path | None = None):
        self.data = data
        self.source = source
        self._visualizer = TreeVisualizer()

    @classmethod
    def from_file(cls, path: str | Path) -> "Config":
        """Create a Config object from a file.

        Args:
            path: Path to the configuration file. Can be a string or Path object.

        Returns:
            A new Config instance containing the loaded configuration data.

        Raises:
            ValueError: If the file format is not supported.
        """
        path = Path(path)
        if path.suffix in [".yaml", ".yml"]:
            with open(path) as f:
                return cls(yaml.safe_load(f), path)
        elif path.suffix == ".json":
            with open(path) as f:
                return cls(json.load(f), path)
        elif path.suffix == ".ini":
            parser = configparser.ConfigParser()
            parser.read(path)
            data = {s: dict(parser.items(s)) for s in parser.sections()}
            return cls(data, path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration data.
        """
        return self.data

    def save(self, path: str | Path | None = None) -> None:
        """Save configuration to a file.

        Args:
            path: Path where to save the configuration. If None, uses the source path.

        Raises:
            ValueError: If no path is specified and source is None.
        """
        path = Path(path) if path else self.source
        if not path:
            raise ValueError("No save path specified")

        with open(path, "w") as f:
            if path.suffix in [".yaml", ".yml"]:
                yaml.dump(self.data, f)
            elif path.suffix == ".json":
                json.dump(self.data, f, indent=2)
            elif path.suffix == ".ini":
                # TODO: Implement INI format conversion logic
                pass

    def visualize(self) -> None:
        """Visualize configuration in a tree structure.

        Displays the configuration data as a hierarchical tree in the console.
        """
        self._visualizer.visualize(self)

    def diff_with(self, config: "Config") -> ConfigDiff:
        """Compare this configuration with another using ConfigDiffer.

        A convenience method that uses ConfigDiffer to analyze differences
        between this configuration and another one.

        Args:
            config: Another Config object to compare with

        Returns:
            ConfigDiff object containing the differences between configurations
        """
        from .differ import ConfigDiffer

        return ConfigDiffer.diff(self, config)

    def __str__(self) -> str:
        """Convert configuration to a string representation.

        Returns:
            String representation of the configuration in a tree structure.
        """
        return self._visualizer.to_string(self)

    def merge_with(
        self, config: "Config", strategy: str = "deep"
    ) -> tuple["Config", list[MergeConflict]]:
        """Merge this configuration with another using ConfigMerger.

        A convenience method that uses ConfigMerger to merge this configuration
        with another one. Similar to diff_with, but for merging.

        Args:
            config: Another Config object to merge with
            strategy: Merge strategy to use ('deep' or 'shallow')
                     'deep' recursively merges nested dictionaries
                     'shallow' only merges top-level keys

        Returns:
            A tuple containing:
            - Config: The merged configuration object
            - list[MergeConflict]: List of merge conflicts detected during merging

        Example:
            >>> config1 = Config.from_file('base.yaml')
            >>> config2 = Config.from_file('override.yaml')
            >>> merged, conflicts = config1.merge_with(config2)
            >>> if conflicts:
            ...     print("Merge conflicts detected:", conflicts)
            >>> merged.save('merged.yaml')
        """
        from .merger import ConfigMerger

        return ConfigMerger.merge([self, config], strategy)
