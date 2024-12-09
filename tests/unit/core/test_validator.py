import json
import tempfile
from pathlib import Path

import jsonschema
import pytest

from configbuddy.core.config import Config
from configbuddy.core.validator import ConfigValidator


class TestConfigValidator:
    @pytest.fixture
    def fxt_sample_schema(self) -> dict:
        """Sample JSON schema for testing"""
        return {
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "required": ["host", "port"],
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "username": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
                "logging": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
                        },
                        "format": {"type": "string"},
                    },
                },
            },
            "required": ["database"],
        }

    @pytest.fixture
    def fxt_schema_file(self, fxt_sample_schema: dict, tmp_path: Path) -> Path:
        """Create a temporary schema file"""
        schema_path = tmp_path / "schema.json"
        with open(schema_path, "w") as f:
            json.dump(fxt_sample_schema, f)
        return schema_path

    def test_validator_initialization(self, fxt_sample_schema):
        """Test validator initialization"""
        validator = ConfigValidator(fxt_sample_schema)
        assert validator.schema == fxt_sample_schema

    def test_validator_from_file(self, fxt_schema_file, fxt_sample_schema):
        """Test creating validator from file"""
        validator = ConfigValidator.from_file(fxt_schema_file)
        assert validator.schema == fxt_sample_schema

    def test_invalid_schema(self):
        """Test exception when initializing with invalid schema"""
        invalid_schema = {"type": "invalid"}
        with pytest.raises(jsonschema.exceptions.SchemaError):
            ConfigValidator(invalid_schema)

    def test_valid_config(self, fxt_sample_schema):
        """Test validation of valid configuration"""
        validator = ConfigValidator(fxt_sample_schema)
        config = Config(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "username": "admin",
                    "password": "secret",
                },
                "logging": {"level": "INFO", "format": "%(asctime)s - %(message)s"},
            }
        )

        result = validator.validate(config)
        assert result is None

    def test_invalid_config_missing_required(self, fxt_sample_schema):
        """Test validation of configuration missing required fields"""
        validator = ConfigValidator(fxt_sample_schema)
        config = Config({"logging": {"level": "INFO"}})

        result = validator.validate(config)
        assert result is not None
        assert any("database" in error for error in result)

    def test_invalid_config_wrong_type(self, fxt_sample_schema):
        """Test validation of configuration with wrong type values"""
        validator = ConfigValidator(fxt_sample_schema)
        config = Config(
            {
                "database": {
                    "host": "localhost",
                    "port": "5432",  # should be integer
                }
            }
        )

        result = validator.validate(config)
        assert result is not None
        assert any("port" in error and "integer" in error for error in result)

    def test_invalid_config_enum_value(self, fxt_sample_schema):
        """Test validation of configuration with invalid enum value"""
        validator = ConfigValidator(fxt_sample_schema)
        config = Config(
            {
                "database": {"host": "localhost", "port": 5432},
                "logging": {
                    "level": "INVALID_LEVEL"  # not in enum
                },
            }
        )

        result = validator.validate(config)
        assert result is not None
        assert any("level" in error and "INVALID_LEVEL" in error for error in result)

    def test_validate_nested_config(self, fxt_sample_schema):
        """Test validation of deeply nested configuration."""
        validator = ConfigValidator(fxt_sample_schema)
        config = Config(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {
                        "username": "admin",
                        "password": "secret",
                        "options": {"ssl": True, "timeout": 30},
                    },
                }
            }
        )

        result = validator.validate(config)
        assert result is None

    def test_validate_array_values(self):
        """Test validation of array type values."""
        schema = {
            "type": "object",
            "properties": {
                "tags": {"type": "array", "items": {"type": "string"}},
                "ports": {"type": "array", "items": {"type": "integer"}},
            },
        }

        validator = ConfigValidator(schema)
        config = Config({"tags": ["dev", "test"], "ports": [8080, 9000]})

        result = validator.validate(config)
        assert result is None

    def test_validate_with_pattern(self):
        """Test validation with regex pattern constraints."""
        schema = {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                },
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
            },
        }

        validator = ConfigValidator(schema)

        # Valid config
        valid_config = Config({"email": "test@example.com", "version": "1.2.3"})
        assert validator.validate(valid_config) is None

        # Invalid email
        invalid_email = Config({"email": "invalid-email", "version": "1.2.3"})
        result = validator.validate(invalid_email)
        assert result is not None
        assert any("email" in error for error in result)

        # Invalid version
        invalid_version = Config({"email": "test@example.com", "version": "1.2"})
        result = validator.validate(invalid_version)
        assert result is not None
        assert any("version" in error for error in result)

    def test_validate_with_dependencies(self):
        """Test validation with property dependencies."""
        schema = {
            "type": "object",
            "properties": {
                "credit_card": {"type": "string"},
                "billing_address": {"type": "string"},
            },
            "dependencies": {"credit_card": ["billing_address"]},
        }

        validator = ConfigValidator(schema)

        # Valid: both present
        valid_config = Config({"credit_card": "1234-5678", "billing_address": "123 Main St"})
        assert validator.validate(valid_config) is None

        # Valid: neither present
        empty_config = Config({})
        assert validator.validate(empty_config) is None

        # Invalid: credit_card without billing_address
        invalid_config = Config({"credit_card": "1234-5678"})
        result = validator.validate(invalid_config)
        assert result is not None
        assert any("dependencies" in error for error in result)

    def test_validate_with_enum_and_const(self):
        """Test validation with enum and const constraints."""
        schema = {
            "type": "object",
            "properties": {
                "mode": {"enum": ["development", "production", "test"]},
                "version": {"const": "1.0.0"},
            },
        }

        validator = ConfigValidator(schema)

        # Valid config
        valid_config = Config({"mode": "development", "version": "1.0.0"})
        assert validator.validate(valid_config) is None

        # Invalid mode
        invalid_mode = Config({"mode": "invalid", "version": "1.0.0"})
        result = validator.validate(invalid_mode)
        assert result is not None
        assert any("mode" in error for error in result)

        # Invalid version
        invalid_version = Config({"mode": "development", "version": "2.0.0"})
        result = validator.validate(invalid_version)
        assert result is not None
        assert any("version" in error for error in result)

    def test_validator_from_invalid_file(self):
        """Test error handling when loading from invalid or non-existent file."""
        with pytest.raises(FileNotFoundError):
            ConfigValidator.from_file("non_existent.json")

        # Invalid JSON file
        with tempfile.NamedTemporaryFile(mode="w") as f:
            f.write("invalid json content")
            f.flush()
            with pytest.raises(json.JSONDecodeError):
                ConfigValidator.from_file(f.name)

    def test_validate_invalid_array_values(self):
        """Test validation of invalid array values."""
        schema = {
            "type": "object",
            "properties": {"numbers": {"type": "array", "items": {"type": "integer"}}},
        }

        validator = ConfigValidator(schema)
        config = Config(
            {
                "numbers": [1, "2", 3]  # "2" is string, not integer
            }
        )

        result = validator.validate(config)
        assert result is not None
        assert any("type" in error and "integer" in error for error in result)

    def test_validate_with_multiple_constraints(self):
        """Test validation with multiple constraints."""
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "score": {
                    "type": "number",
                    "multipleOf": 0.5,
                    "minimum": 0,
                    "maximum": 100,
                },
            },
        }

        validator = ConfigValidator(schema)

        # Valid config
        valid_config = Config({"age": 25, "score": 95.5})
        assert validator.validate(valid_config) is None

        # Invalid age
        invalid_age = Config({"age": -1, "score": 95.5})
        result = validator.validate(invalid_age)
        assert result is not None
        assert any("minimum" in error for error in result)

        # Invalid score
        invalid_score = Config(
            {
                "age": 25,
                "score": 95.7,  # not multiple of 0.5
            }
        )
        result = validator.validate(invalid_score)
        assert result is not None
        assert any("multipleOf" in error for error in result)

    def test_validate_additional_properties(self):
        """Test validation with additionalProperties constraint."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": False,
        }

        validator = ConfigValidator(schema)

        # Valid config
        valid_config = Config({"name": "test"})
        assert validator.validate(valid_config) is None

        # Invalid with additional property
        invalid_config = Config({"name": "test", "extra": "not allowed"})
        result = validator.validate(invalid_config)
        assert result is not None
        assert any("additional properties" in error.lower() for error in result)

    def test_generate_schema_from_config(self):
        """Test schema generation from configuration."""
        config = Config(
            {
                "server": {
                    "host": "localhost",
                    "port": 8080,
                    "debug": True,
                    "tags": ["api", "v1"],
                    "timeout": 30.5,
                    "options": {"ssl": True, "workers": 4},
                },
                "database": None,
                "features": [
                    {
                        "name": "feature1",
                        "enabled": True,
                        "params": {"scale": True, "threshold": 0.5},
                    },
                    {
                        "name": "feature2",
                        "enabled": False,
                        "params": {"scale": "large", "threshold": 0.8},
                    },
                ],
            }
        )

        validator = ConfigValidator.from_config(config)
        schema = validator.schema

        # Debug output
        print("\nGenerated Schema:", json.dumps(schema, indent=2))

        # Check basic schema structure
        assert schema["type"] == "object"
        assert "$schema" in schema
        assert "properties" in schema

        # Check server section
        server = schema["properties"]["server"]
        assert server["type"] == "object"
        assert "properties" in server
        server_props = server["properties"]
        assert server_props["host"]["type"] == "string"
        assert server_props["port"]["type"] == "integer"
        assert server_props["debug"]["type"] == "boolean"
        assert server_props["timeout"]["type"] == "number"

        # Check array handling
        tags = server_props["tags"]
        assert tags["type"] == "array"
        assert tags["items"]["type"] == "string"

        # Check nested object
        options = server_props["options"]
        assert options["type"] == "object"
        assert "properties" in options
        option_props = options["properties"]
        assert option_props["ssl"]["type"] == "boolean"
        assert option_props["workers"]["type"] == "integer"

        # Check null handling
        assert schema["properties"]["database"]["type"] == "null"

        # Check complex array with objects
        features = schema["properties"]["features"]
        assert features["type"] == "array"
        feature_items = features["items"]
        assert feature_items["type"] == "object"
        assert "properties" in feature_items
        feature_props = feature_items["properties"]

        # Debug output for feature properties
        print("\nFeature Properties:", json.dumps(feature_props, indent=2))

        # Check params object
        params = feature_props["params"]
        assert "anyOf" in params

        # Check each possible params schema
        param_schemas = params["anyOf"]
        assert len(param_schemas) == 2

        # Each schema should be an object type with properties
        for param_schema in param_schemas:
            assert param_schema["type"] == "object"
            assert "properties" in param_schema
            props = param_schema["properties"]

            # Both schemas should have threshold as number
            assert props["threshold"]["type"] == "number"

            # Scale can be either boolean or string
            assert props["scale"]["type"] in {"boolean", "string"}

        # Verify that we have both boolean and string types for scale
        scale_types = {schema["properties"]["scale"]["type"] for schema in param_schemas}
        assert scale_types == {"boolean", "string"}

    def test_generate_schema_with_empty_config(self):
        """Test schema generation from empty configuration."""
        config = Config({})
        validator = ConfigValidator.from_config(config)
        schema = validator.schema

        assert schema["type"] == "object"
        assert "$schema" in schema
        assert "properties" in schema
        assert isinstance(schema["properties"], dict)
        assert len(schema["properties"]) == 0

    def test_generate_schema_with_arrays(self):
        """Test schema generation with various array types."""
        config = Config(
            {
                "empty_array": [],
                "number_array": [1, 2, 3],
                "mixed_array": [1, "two", True],
                "object_array": [
                    {"id": 1, "name": "first"},
                    {"id": 2, "name": "second", "extra": True},
                ],
            }
        )

        validator = ConfigValidator.from_config(config)
        schema = validator.schema

        # Check empty array
        empty = schema["properties"]["empty_array"]
        assert empty["type"] == "array"
        assert empty["items"] == {}

        # Check number array
        numbers = schema["properties"]["number_array"]
        assert numbers["type"] == "array"
        assert numbers["items"]["type"] == "integer"

        # Check mixed array
        mixed = schema["properties"]["mixed_array"]
        assert mixed["type"] == "array"
        assert "anyOf" in mixed["items"]
        mixed_types = {t["type"] for t in mixed["items"]["anyOf"]}
        assert mixed_types == {"integer", "string", "boolean"}

        # Check object array
        objects = schema["properties"]["object_array"]
        assert objects["type"] == "array"
        items = objects["items"]
        assert items["type"] == "object"
        assert "properties" in items
        item_props = items["properties"]
        assert item_props["id"]["type"] == "integer"
        assert item_props["name"]["type"] == "string"
        assert item_props["extra"]["type"] == "boolean"
