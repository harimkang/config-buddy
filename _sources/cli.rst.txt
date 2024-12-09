Command Line Interface
====================

ConfigBuddy provides a powerful command-line interface (CLI) for managing configuration files.

Commands
--------

visualize
~~~~~~~~~

Visualize a configuration file in a tree format:

.. code-block:: bash

    configbuddy visualize <config_file>

Options:
    - ``--style``: Tree style (ascii, bold, double, or rounded)

diff
~~~~

Compare two configuration files and show their differences:

.. code-block:: bash

    configbuddy diff <base_file> --compare <other_file>

Options:
    - ``--style``: Tree style for visualization
    - ``--output-format``: Output format (tree or json)

merge
~~~~~

Merge two configuration files:

.. code-block:: bash

    configbuddy merge <base_file> <override_file> -o <output_file>

Options:
    - ``--strategy``: Merge strategy (deep or shallow)
    - ``-o, --output``: Output file path

validate
~~~~~~~~

Validate a configuration file against a JSON schema:

.. code-block:: bash

    configbuddy validate <config_file> --schema <schema_file>

Options:
    - ``--schema``: JSON schema file path

generate-schema
~~~~~~~~~~~~~~

Generate a JSON schema from a configuration file:

.. code-block:: bash

    configbuddy generate-schema <config_file> -o <schema_file>

Options:
    - ``-o, --output``: Output schema file path

Global Options
-------------

These options are available for all commands:

- ``--help``: Show help message
- ``--version``: Show version information
- ``--verbose``: Enable verbose output

Examples
--------

1. Visualize a YAML configuration with rounded style:

   .. code-block:: bash

       configbuddy visualize config.yaml --style rounded

2. Compare configurations and output as JSON:

   .. code-block:: bash

       configbuddy diff base.yaml --compare other.yaml --output-format json

3. Merge configurations with deep strategy:

   .. code-block:: bash

       configbuddy merge base.yaml override.yaml -o merged.yaml --strategy deep

4. Validate configuration against schema:

   .. code-block:: bash

       configbuddy validate config.yaml --schema schema.json 