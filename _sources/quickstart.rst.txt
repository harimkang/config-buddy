Quickstart Guide
===============

This guide will help you get started with ConfigBuddy quickly.

Basic Usage
----------

1. Load a configuration file:

.. code-block:: python

    from configbuddy import Config

    # Load from YAML
    config = Config.from_file('config.yaml')

    # Or from JSON
    config = Config.from_file('config.json')

2. Visualize configuration:

.. code-block:: python

    # Print configuration as a tree
    config.visualize()

3. Compare configurations:

.. code-block:: python

    config1 = Config.from_file('config1.yaml')
    config2 = Config.from_file('config2.yaml')

    # Compare configurations
    diff = config1.diff_with(config2)
    
    # Visualize differences
    diff.visualize()

4. Merge configurations:

.. code-block:: python

    # Merge with another configuration
    merged, conflicts = config1.merge_with(config2)

    if conflicts:
        print("Merge conflicts:", conflicts)
    else:
        merged.save('merged.yaml')

5. Validate configuration:

.. code-block:: python

    from configbuddy import ConfigValidator

    # Create validator with schema
    validator = ConfigValidator.from_file('schema.json')

    # Validate configuration
    is_valid = validator.validate(config)

    if not is_valid:
        print("Validation errors:", validator.errors)

CLI Usage
---------

ConfigBuddy also provides a powerful CLI interface. Here are some common commands:

1. Visualize a configuration:

.. code-block:: bash

    configbuddy visualize config.yaml

2. Compare configurations:

.. code-block:: bash

    configbuddy diff base.yaml --compare other.yaml

3. Merge configurations:

.. code-block:: bash

    configbuddy merge base.yaml override.yaml -o merged.yaml

4. Validate configuration:

.. code-block:: bash

    configbuddy validate config.yaml --schema schema.json

For more detailed information about the CLI, see the :doc:`cli` section. 