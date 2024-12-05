# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Protocol
from rich.tree import Tree
from rich.console import Console
from io import StringIO
from .types import ConfigDiff


class ConfigData(Protocol):
    """Protocol for configuration data.

    This protocol defines the required interface for configuration data objects
    that can be visualized by the TreeVisualizer.

    Attributes:
        data: Dictionary containing the configuration data
        source: Optional path to the source configuration file
    """

    @property
    def data(self) -> dict[str, Any]:
        ...

    @property
    def source(self) -> Path | None:
        ...


class BaseVisualizer(ABC):
    """Base class for configuration visualizers.

    This abstract class defines the interface that all visualizer implementations must follow.
    It provides common functionality for displaying configuration data in different formats.
    """

    @abstractmethod
    def visualize(self, data: Any) -> None:
        """Display data in the console.

        Args:
            data: The data to visualize. The specific type depends on the visualizer implementation.
        """
        pass

    @abstractmethod
    def to_string(self, data: Any) -> str:
        """Convert visualization to string.

        Args:
            data: The data to convert to string representation

        Returns:
            String representation of the visualized data
        """
        pass

    def _create_console(self, string_io: StringIO | None = None) -> Console:
        """Create a console instance for output.

        Args:
            string_io: Optional StringIO object to write output to instead of terminal

        Returns:
            Console instance configured for either terminal or string output
        """
        return Console(file=string_io, force_terminal=False if string_io else True)


class TreeVisualizer(BaseVisualizer):
    """Visualizer for configuration data in tree structure.

    This visualizer displays configuration data as a colored tree structure,
    with different colors for each level of nesting and different data types.
    """

    def __init__(self) -> None:
        """Initialize the TreeVisualizer with a predefined set of colors for different tree levels."""
        self.level_colors = [
            "turquoise2",
            "orchid2",
            "medium_spring_green",
            "tan",
            "deep_sky_blue3",
        ]

    def _build_tree(self, tree: Tree, data: dict[str, Any], depth: int = 0) -> None:
        """Helper function to recursively build a rich.tree.Tree object.

        Args:
            tree: The Tree object to build upon
            data: Dictionary containing configuration data
            depth: Current depth in the tree hierarchy (used for color selection)
        """
        color = self.level_colors[depth % len(self.level_colors)]

        for key, value in data.items():
            if isinstance(value, dict):
                # Apply level-specific color for dictionary nodes
                branch = tree.add(f"[bold {color}]{key}[/]")
                self._build_tree(branch, value, depth + 1)
            elif isinstance(value, list):
                # Apply level-specific color for list nodes
                branch = tree.add(f"[bold {color}]{key}[/]")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        item_branch = branch.add(f"[{color}][{i}][/]")
                        self._build_tree(item_branch, item, depth + 1)
                    else:
                        # Display list items in gray
                        formatted_value = self._format_value(item)
                        branch.add(f"[{color}][{i}][/]: {formatted_value}")
            else:
                # Apply level color for keys and type-specific color for values
                formatted_value = self._format_value(value)
                tree.add(f"[{color}]{key}[/]: {formatted_value}")

    def _format_value(self, value: Any) -> str:
        """Format value with appropriate color based on its type.

        Args:
            value: The value to format

        Returns:
            A string with rich markup for colored formatting based on the value type:
            - Numbers (int/float): white
            - Strings: yellow with quotes
            - None: dimmed "null"
            - Booleans: blue lowercase
            - Other types: red
        """
        if isinstance(value, (int, float)):
            return f"[white]{value}[/]"
        elif isinstance(value, str):
            return f'[yellow]"{value}"[/]'
        elif value is None:
            return "[dim]null[/]"
        elif isinstance(value, bool):
            return f"[blue]{str(value).lower()}[/]"
        else:
            return f"[red]{value}[/]"

    def _create_tree(self, source: Path | None) -> Tree:
        """Create a new Tree object with the given source as root.

        Args:
            source: Optional source path to display as root node

        Returns:
            A new Tree instance with formatted root node and black guide lines
        """
        return Tree(
            f"[bold white]{source if source else 'Config'}[/]",
            guide_style="bright_black",
        )

    def visualize(self, config: ConfigData) -> None:
        """Display the configuration data as a tree in the console.

        Args:
            config: Configuration data object implementing the ConfigData protocol
        """
        console = self._create_console()
        tree = self._create_tree(config.source)
        self._build_tree(tree, config.data)
        console.print(tree)

    def to_string(self, config: ConfigData) -> str:
        """Convert the configuration tree visualization to a string.

        Args:
            config: Configuration data object implementing the ConfigData protocol

        Returns:
            String representation of the configuration tree visualization
        """
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=False)
        tree = self._create_tree(config.source)
        self._build_tree(tree, config.data)
        console.print(tree)
        return string_io.getvalue()


class DiffVisualizer(BaseVisualizer):
    """Visualizer for configuration differences.

    This visualizer displays the differences between two configurations,
    highlighting added, removed, and modified values in different colors.
    """

    def _build_diff_tree(self, tree: Tree, data: dict[str, Any], style: str) -> None:
        """Helper function to recursively build a diff tree with specified style.

        Args:
            tree: The Tree object to build upon
            data: Dictionary containing diff data
            style: Color style to apply to the nodes (e.g., "green" for additions)
        """
        for key, value in data.items():
            if isinstance(value, dict):
                branch = tree.add(f"[{style}]{key}[/]")
                self._build_diff_tree(branch, value, style)
            elif isinstance(value, list):
                branch = tree.add(f"[{style}]{key}[/]")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        item_branch = branch.add(f"[{style}][{i}][/]")
                        self._build_diff_tree(item_branch, item, style)
                    else:
                        branch.add(f"[{style}][{i}]: {self._format_value(item)}[/]")
            else:
                tree.add(f"[{style}]{key}: {self._format_value(value)}[/]")

    def _format_value(self, value: Any) -> str:
        """Format value with appropriate color based on its type."""
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif value is None:
            return "null"
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    def _build_modified_tree(
        self, tree: Tree, data: dict[str, tuple[Any, Any]]
    ) -> None:
        """Helper function to build a tree for modified values.

        Args:
            tree: The Tree object to build upon
            data: Dictionary containing pairs of old and new values
                 where key maps to tuple of (old_value, new_value)
        """
        for key, (old, new) in data.items():
            branch = tree.add(f"[yellow]{key}[/]")
            branch.add(f"[red]- {old}[/]")
            branch.add(f"[green]+ {new}[/]")

    def visualize(self, diff: ConfigDiff) -> None:
        """Display the configuration differences in the console.

        Args:
            diff: ConfigDiff object containing added, removed, modified, and unchanged items
        """
        console = self._create_console()
        tree = Tree("Configuration Differences")
        self._build_diff_sections(tree, diff)
        console.print(tree)

    def to_string(self, diff: ConfigDiff) -> str:
        """Convert the configuration differences visualization to a string.

        Args:
            diff: ConfigDiff object containing added, removed, modified, and unchanged items

        Returns:
            String representation of the configuration differences visualization
        """
        string_io = StringIO()
        console = self._create_console(string_io)
        tree = Tree("Configuration Differences")
        self._build_diff_sections(tree, diff)
        console.print(tree)
        return string_io.getvalue()

    def _build_diff_sections(self, tree: Tree, diff: ConfigDiff) -> None:
        """Build all sections of the diff tree.

        Creates separate sections for added (green), removed (red), and modified (yellow) items.
        Each section is color-coded and contains the respective changes.

        Args:
            tree: The Tree object to build upon
            diff: ConfigDiff object containing the differences to visualize
        """
        if diff.added:
            added = tree.add("[green]Added[/]")
            self._build_diff_tree(added, diff.added, "green")

        if diff.removed:
            removed = tree.add("[red]Removed[/]")
            self._build_diff_tree(removed, diff.removed, "red")

        if diff.modified:
            modified = tree.add("[yellow]Modified[/]")
            self._build_modified_tree(modified, diff.modified)

        # TODO: How to visualize unchanged?
        # if diff.unchanged:
        #     unchanged = tree.add("[bright_black]Unchanged[/]")
        #     self._build_diff_tree(unchanged, diff.unchanged, "bright_black")
