# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

from typing import Any

from .config import Config
from .types import MergeConflict


class ConfigMerger:
    """Class for merging multiple configuration files.

    This class provides functionality to merge multiple Config objects,
    with support for different merge strategies and conflict detection.

    The merger supports two strategies:
    - deep: Recursively merges nested dictionaries
    - shallow: Only merges top-level keys

    When conflicts are detected during merging, they are tracked and returned
    along with the merged result. A conflict occurs when multiple configs have
    different values for the same key.
    """

    @staticmethod
    def merge(configs: list[Config], strategy: str = "deep") -> tuple[Config, list[MergeConflict]]:
        """Merge multiple configuration files.

        Args:
            configs: List of Config objects to merge. Must contain at least one config.
            strategy: Merge strategy to use. Can be either 'deep' or 'shallow'.
                     'deep' recursively merges nested dictionaries.
                     'shallow' only merges top-level keys.

        Returns:
            A tuple containing:
            - Config: The merged configuration object
            - list[MergeConflict]: List of merge conflicts detected during merging

        Raises:
            ValueError: If no configs provided or if strategy is not 'deep' or 'shallow'
        """
        if not configs:
            raise ValueError("No configs to merge")

        result_data: dict[str, Any] = {}
        conflicts: list[MergeConflict] = []

        if strategy == "deep":
            result_data = ConfigMerger._deep_merge(
                [config.to_dict() for config in configs],
                [str(config.source) for config in configs],
                conflicts,
            )
        elif strategy == "shallow":
            result_data = ConfigMerger._shallow_merge(
                [config.to_dict() for config in configs],
                [str(config.source) for config in configs],
                conflicts,
            )
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")

        return Config(result_data), conflicts

    @staticmethod
    def _deep_merge(dicts: list[dict[str, Any]], sources: list[str], conflicts: list[MergeConflict]) -> dict[str, Any]:
        """Recursively merge dictionaries with conflict detection.

        This method performs a deep merge of multiple dictionaries, recursively merging
        nested dictionary structures. When conflicts are found, they are recorded and
        the last value is used in the merged result.

        Args:
            dicts: List of dictionaries to merge
            sources: List of source identifiers corresponding to each dictionary
            conflicts: List to store detected merge conflicts

        Returns:
            A merged dictionary containing values from all input dictionaries.
            For conflicting values, the last value in the input list is used.
        """
        result: dict[str, Any] = {}

        # Collect all keys
        all_keys = {key for d in dicts for key in d.keys()}

        for key in all_keys:
            # Collect values for this key from each config
            values = [(d.get(key), src) for d, src in zip(dicts, sources, strict=False) if key in d]

            if len(values) == 1:
                # No conflict: key exists in only one config
                result[key] = values[0][0]
            else:
                # Split values and their sources
                vals, srcs = zip(*values, strict=False)

                if all(isinstance(v, dict) for v in vals):
                    # If all values are dictionaries, merge recursively
                    result[key] = ConfigMerger._deep_merge(list(vals), srcs, conflicts)
                elif all(str(vals[0]) == str(v) for v in vals):
                    # All values are identical (using string comparison)
                    result[key] = vals[0]
                else:
                    # Conflict detected
                    conflicts.append(MergeConflict(key, list(vals), list(srcs)))
                    # Use the last value
                    result[key] = vals[-1]

        return result

    @staticmethod
    def _shallow_merge(
        dicts: list[dict[str, Any]], sources: list[str], conflicts: list[MergeConflict]
    ) -> dict[str, Any]:
        """Merge dictionaries at top level only.

        This method performs a shallow merge of multiple dictionaries, only combining
        top-level keys. Nested structures are not recursively merged. When conflicts
        are found, they are recorded and the last value is used in the merged result.

        Args:
            dicts: List of dictionaries to merge
            sources: List of source identifiers corresponding to each dictionary
            conflicts: List to store detected merge conflicts

        Returns:
            A merged dictionary containing values from all input dictionaries.
            For conflicting values, the last value in the input list is used.
            Nested dictionaries are not merged - the entire dictionary from the
            last source is used.
        """
        result: dict[str, Any] = {}

        # Collect all keys
        all_keys = {key for d in dicts for key in d.keys()}

        for key in all_keys:
            # Collect values for this key from each config
            values = [(d.get(key), src) for d, src in zip(dicts, sources, strict=False) if key in d]

            if len(values) == 1:
                # No conflict
                result[key] = values[0][0]
            else:
                # Split values and their sources
                vals, srcs = zip(*values, strict=False)
                if len(set(str(v) for v in vals)) == 1:
                    # All values are identical
                    result[key] = vals[0]
                else:
                    # Conflict detected
                    conflicts.append(MergeConflict(key, list(vals), list(srcs)))
                    # Use the last value
                    result[key] = vals[-1]

        return result
