# Copyright (c) 2024 Harim Kang
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

from .config import Config


class ConfigValidator:
    """Class for validating configuration files.

    This class provides functionality to validate configuration data against a JSON schema.
    """

    def __init__(self, schema: dict[str, Any]):
        """Initialize validator with a schema.

        Args:
            schema: JSON schema dictionary to validate against

        Raises:
            jsonschema.exceptions.SchemaError: If the schema itself is invalid
        """
        self.schema = schema
        Draft7Validator.check_schema(schema)

    @classmethod
    def from_file(cls, schema_path: str | Path) -> "ConfigValidator":
        """Create a validator from a schema file.

        Args:
            schema_path: Path to the JSON schema file

        Returns:
            ConfigValidator instance initialized with the schema from file
        """
        with open(schema_path) as f:
            schema = json.load(f)
        return cls(schema)

    def validate(self, config: Config) -> list[str] | None:
        """Validate a configuration against the schema."""
        try:
            validator = Draft7Validator(self.schema)
            validator.validate(config.to_dict())
            return None
        except jsonschema.exceptions.ValidationError as e:
            print(f"Debug - Schema: {json.dumps(self.schema, indent=2)}")  # Temporary debug
            print(f"Debug - Config: {json.dumps(config.to_dict(), indent=2)}")  # Temporary debug
            print(f"Debug - Error: {e}")  # Temporary debug
            return [str(e)]

    @classmethod
    def generate_schema(cls, config: Config) -> dict[str, Any]:
        """Generate a JSON schema from a configuration file."""

        def _merge_types(type1: dict[str, Any], type2: dict[str, Any]) -> dict[str, Any]:
            """Merge two type definitions into one."""
            if type1 == type2:
                return type1

            # Special handling for number types
            def get_number_type(t: dict[str, Any]) -> str | None:
                type_val = t.get("type")
                if isinstance(type_val, str) and type_val in ("integer", "number"):
                    return type_val
                return None

            # If both are number types, use the more general one
            num_type1 = get_number_type(type1)
            num_type2 = get_number_type(type2)
            if num_type1 and num_type2:
                return {"type": "number" if "number" in (num_type1, num_type2) else "integer"}

            # Extract types from anyOf if present
            types1 = type1.get("anyOf", [type1])
            types2 = type2.get("anyOf", [type2])

            # Combine all unique types
            all_types: list[dict[str, Any]] = []
            for t in types1 + types2:
                if t not in all_types:
                    all_types.append(t)

            # If only one type remains, return it directly
            if len(all_types) == 1:
                return all_types[0]

            # Otherwise, return anyOf with all types
            return {"anyOf": all_types}

        def _merge_multiple_types(types: list[dict[str, Any]]) -> dict[str, Any]:
            """Merge multiple type definitions into one."""
            if not types:
                return {}
            if len(types) == 1:
                return types[0]

            result = types[0]
            for t in types[1:]:
                result = _merge_types(result, t)
            return result

        def _infer_type(value: Any) -> dict[str, Any]:
            if isinstance(value, dict):
                # For each property, collect all types from all objects
                props = {k: _infer_type(v) for k, v in value.items()}

                schema = {
                    "type": "object",
                    "properties": props,
                    "additionalProperties": True,
                }
                return schema
            elif isinstance(value, list):
                if not value:  # Empty list
                    return {"type": "array", "items": {}}
                if isinstance(value[0], dict):
                    # For array of objects, create a common schema
                    # First, collect all unique keys and their types
                    key_types: dict[str, set[str]] = {}
                    for item in value:
                        if not isinstance(item, dict):
                            continue
                        for k, v in item.items():
                            type_def = _infer_type(v)
                            type_str = str(type_def)
                            if k not in key_types:
                                key_types[k] = {type_str}
                            else:
                                key_types[k].add(type_str)

                    # Then create merged schema for each key
                    obj_props: dict[str, Any] = {}
                    for k, types in key_types.items():
                        type_defs = [eval(t) for t in types]
                        if len(type_defs) == 1:
                            obj_props[k] = type_defs[0]
                        else:
                            obj_props[k] = {"anyOf": type_defs}

                    return {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": obj_props,
                            "additionalProperties": True,
                        },
                    }
                else:
                    # For array of primitives, merge all types
                    item_types = [_infer_type(item) for item in value]
                    return {"type": "array", "items": _merge_multiple_types(item_types)}
            elif isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                return {"type": "string"}
            elif value is None:
                return {"type": "null"}
            else:
                return {"type": "string"}

        data = config.to_dict()
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {k: _infer_type(v) for k, v in data.items()},
            "additionalProperties": True,
        }
        return schema

    @classmethod
    def from_config(cls, config: Config) -> "ConfigValidator":
        """Create a validator from an existing configuration.

        Args:
            config: Configuration object to generate schema from

        Returns:
            ConfigValidator instance with schema generated from config
        """
        schema = cls.generate_schema(config)
        return cls(schema)

    def save_schema(self, path: str | Path) -> None:
        """Save the current schema to a file.

        Args:
            path: Path where to save the schema
        """
        with open(path, "w") as f:
            json.dump(self.schema, f, indent=2)
