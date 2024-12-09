import tempfile
from pathlib import Path

import pytest

from configbuddy.core.config import Config


class TestConfig:
    @pytest.fixture
    def sample_dict_data(self):
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "admin", "password": "secret"},
            },
            "logging": {"level": "INFO", "format": "%(asctime)s - %(message)s"},
        }

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    def test_config_initialization(self, sample_dict_data):
        """Test if Config object is properly initialized with data"""
        config = Config(sample_dict_data)
        assert config.data == sample_dict_data
        assert config.source is None

    def test_config_initialization_with_source(self, sample_dict_data):
        """Test if Config object is properly initialized with source path"""
        source = Path("config.yaml")
        config = Config(sample_dict_data, source)
        assert config.data == sample_dict_data
        assert config.source == source

    def test_from_yaml_file(self, temp_dir, sample_dict_data):
        """Test creating Config object from YAML file"""
        yaml_path = temp_dir / "config.yaml"
        with open(yaml_path, "w") as f:
            f.write(
                """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
logging:
  level: INFO
  format: "%(asctime)s - %(message)s"
            """.strip()
            )

        config = Config.from_file(yaml_path)
        assert config.data == sample_dict_data
        assert config.source == yaml_path

    def test_from_json_file(self, temp_dir, sample_dict_data):
        """Test creating Config object from JSON file"""
        json_path = temp_dir / "config.json"
        with open(json_path, "w") as f:
            f.write(
                """
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(message)s"
    }
}
            """.strip()
            )

        config = Config.from_file(json_path)
        assert config.data == sample_dict_data
        assert config.source == json_path

    def test_from_ini_file(self, temp_dir):
        """Test creating Config object from INI file"""
        ini_path = temp_dir / "config.ini"
        with open(ini_path, "w") as f:
            f.write(
                """
[database]
host = localhost
port = 5432
username = admin
password = secret

[logging]
level = INFO
format = %%(asctime)s - %%(message)s
            """.strip()
            )

        config = Config.from_file(ini_path)
        assert config.data["database"]["host"] == "localhost"
        assert config.data["database"]["port"] == "5432"  # INI files are read as strings
        assert config.data["logging"]["level"] == "INFO"
        assert config.source == ini_path

    def test_unsupported_file_format(self, temp_dir):
        """Test exception handling for unsupported file formats"""
        unsupported_path = temp_dir / "config.txt"
        unsupported_path.touch()

        with pytest.raises(ValueError, match="Unsupported file format: .txt"):
            Config.from_file(unsupported_path)

    def test_save_yaml(self, temp_dir, sample_dict_data):
        """Test saving configuration in YAML format"""
        config = Config(sample_dict_data)
        save_path = temp_dir / "saved_config.yaml"

        config.save(save_path)
        loaded_config = Config.from_file(save_path)
        assert loaded_config.data == sample_dict_data

    def test_save_json(self, temp_dir, sample_dict_data):
        """Test saving configuration in JSON format"""
        config = Config(sample_dict_data)
        save_path = temp_dir / "saved_config.json"

        config.save(save_path)
        loaded_config = Config.from_file(save_path)
        assert loaded_config.data == sample_dict_data

    def test_save_without_path(self, temp_dir, sample_dict_data):
        """Test exception handling when no save path is specified"""
        config = Config(sample_dict_data)  # source is None

        with pytest.raises(ValueError, match="No save path specified"):
            config.save()

    def test_save_to_source_path(self, temp_dir, sample_dict_data):
        """Test saving configuration to original source path"""
        original_path = temp_dir / "config.yaml"
        config = Config(sample_dict_data, source=original_path)

        config.save()  # Save to original path
        loaded_config = Config.from_file(original_path)
        assert loaded_config.data == sample_dict_data

    def test_to_dict(self, sample_dict_data):
        """Test dictionary conversion"""
        config = Config(sample_dict_data)
        assert config.to_dict() == sample_dict_data

    def test_merge_with(self):
        """Test merging configurations using merge_with method."""
        config1 = Config({"database": {"host": "localhost", "port": 5432}}, Path("config1.yaml"))

        config2 = Config(
            {"database": {"host": "127.0.0.1", "username": "admin"}},
            Path("config2.yaml"),
        )

        # Test deep merge
        merged, conflicts = config1.merge_with(config2)
        assert merged.data["database"]["host"] == "127.0.0.1"  # Takes override value
        assert merged.data["database"]["port"] == 5432  # Keeps original value
        assert merged.data["database"]["username"] == "admin"  # Adds new value
        assert len(conflicts) == 1  # Conflict for 'host'

        # Test shallow merge
        merged, conflicts = config1.merge_with(config2, strategy="shallow")
        assert merged.data["database"] == config2.data["database"]  # Takes entire override section
        assert len(conflicts) == 1  # Conflict for 'database'
