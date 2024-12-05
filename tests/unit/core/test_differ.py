from configbuddy import Config
from configbuddy.core.differ import ConfigDiffer


def test_diff_identical_configs():
    """Test comparing identical configuration files"""
    data = {"database": {"host": "localhost", "port": 5432}}

    base = Config(data.copy())
    other = Config(data.copy())

    diff = ConfigDiffer.diff(base, other)

    assert not diff.added
    assert not diff.removed
    assert not diff.modified
    assert diff.unchanged == data


def test_diff_added_keys():
    """Test when new keys are added"""
    base_data = {"database": {"host": "localhost"}}

    other_data = {
        "database": {
            "host": "localhost",
            "port": 5432,  # newly added key
        }
    }

    base = Config(base_data)
    other = Config(other_data)

    diff = ConfigDiffer.diff(base, other)

    assert "database" in diff.modified
    assert diff.modified["database"][1]["port"] == 5432
    assert not diff.removed
    assert not diff.added


def test_diff_removed_keys():
    """Test when keys are removed"""
    base_data = {"database": {"host": "localhost", "port": 5432}}

    other_data = {
        "database": {
            "host": "localhost"  # port key removed
        }
    }

    base = Config(base_data)
    other = Config(other_data)

    diff = ConfigDiffer.diff(base, other)

    assert "database" in diff.modified
    assert "port" in diff.modified["database"][0]
    assert not diff.added
    assert not diff.removed


def test_diff_modified_values():
    """Test when values are modified"""
    base_data = {"database": {"host": "localhost", "port": 5432}}

    other_data = {
        "database": {
            "host": "127.0.0.1",  # value changed
            "port": 5432,
        }
    }

    base = Config(base_data)
    other = Config(other_data)

    diff = ConfigDiffer.diff(base, other)

    assert "database" in diff.modified
    assert diff.modified["database"][0]["host"] == "localhost"
    assert diff.modified["database"][1]["host"] == "127.0.0.1"
    assert not diff.added
    assert not diff.removed


def test_diff_completely_different_configs():
    """Test comparing completely different configuration files"""
    base_data = {"database": {"host": "localhost", "port": 5432}}

    other_data = {"logging": {"level": "DEBUG", "format": "%(asctime)s - %(message)s"}}

    base = Config(base_data)
    other = Config(other_data)

    diff = ConfigDiffer.diff(base, other)

    assert "logging" in diff.added
    assert "database" in diff.removed
    assert not diff.modified
    assert not diff.unchanged


def test_diff_nested_structures():
    """Test comparing nested configuration structures"""
    base_data = {
        "database": {
            "primary": {"host": "localhost", "port": 5432},
            "replica": {"host": "replica.host", "port": 5432},
        }
    }

    other_data = {
        "database": {
            "primary": {
                "host": "localhost",
                "port": 5433,  # port changed
            },
            "replica": {"host": "replica.host", "port": 5432},
        }
    }

    base = Config(base_data)
    other = Config(other_data)

    diff = ConfigDiffer.diff(base, other)

    assert "database" in diff.modified
    assert diff.modified["database"][0]["primary"]["port"] == 5432
    assert diff.modified["database"][1]["primary"]["port"] == 5433
    assert not diff.added
    assert not diff.removed
