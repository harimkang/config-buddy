# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Any


@dataclass
class ConfigDiff:
    """Class representing differences between configuration files.

    Attributes:
        added: Dictionary of keys and values that were added in the new config
        removed: Dictionary of keys and values that were removed from the base config
        modified: Dictionary of keys mapping to tuples of (old_value, new_value)
        unchanged: Dictionary of keys and values that remained the same
    """

    added: dict[str, Any]
    removed: dict[str, Any]
    modified: dict[str, tuple[Any, Any]]  # (old_value, new_value)
    unchanged: dict[str, Any]

    def visualize(self) -> None:
        """Visualize the configuration differences in a tree structure."""
        from .visualizer import DiffVisualizer

        visualizer = DiffVisualizer()
        visualizer.visualize(self)

    def __str__(self) -> str:
        """Return a string representation of the configuration differences."""
        from .visualizer import DiffVisualizer

        visualizer = DiffVisualizer()
        return visualizer.to_string(self)


@dataclass
class MergeConflict:
    """Class representing a merge conflict between configurations.

    Attributes:
        key: The configuration key where the conflict occurred
        values: List of conflicting values from different sources
        sources: List of source identifiers where the conflicting values came from
    """

    key: str
    values: list[Any]
    sources: list[str]
