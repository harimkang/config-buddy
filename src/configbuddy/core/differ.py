# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

from .config import Config
from .types import ConfigDiff


class ConfigDiffer:
    """Class for comparing and finding differences between configuration files."""

    @staticmethod
    def diff(base: Config, other: Config) -> ConfigDiff:
        """Analyze differences between two configuration files.

        Args:
            base: The base configuration to compare against
            other: The other configuration to compare with

        Returns:
            ConfigDiff object containing the added, removed, modified and unchanged items
        """
        base_dict = base.to_dict()
        other_dict = other.to_dict()

        added = {}
        removed = {}
        modified = {}
        unchanged = {}

        # Recursively compare all keys
        all_keys = set(base_dict.keys()) | set(other_dict.keys())
        for key in all_keys:
            if key not in base_dict:
                added[key] = other_dict[key]
            elif key not in other_dict:
                removed[key] = base_dict[key]
            elif base_dict[key] != other_dict[key]:
                modified[key] = (base_dict[key], other_dict[key])
            else:
                unchanged[key] = base_dict[key]

        return ConfigDiff(added, removed, modified, unchanged)
