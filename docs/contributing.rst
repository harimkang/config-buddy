Contributing Guide
=================

Thank you for considering contributing to ConfigBuddy! This document provides guidelines and instructions for contributing.

Development Setup
---------------

1. Fork and clone the repository:

   .. code-block:: bash

       git clone https://github.com/your-username/configbuddy.git
       cd configbuddy

2. Create a virtual environment:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies:

   .. code-block:: bash

       pip install -e ".[dev]"

4. Install pre-commit hooks:

   .. code-block:: bash

       pre-commit install

Code Style
---------

We use the following tools to maintain code quality:

- ``black``: Code formatting
- ``isort``: Import sorting
- ``ruff``: Linting
- ``mypy``: Type checking

These checks are automatically run by pre-commit hooks.

Running Tests
------------

Run tests using pytest:

.. code-block:: bash

    pytest

For coverage report:

.. code-block:: bash

    pytest --cov=configbuddy

Pull Request Process
------------------

1. Create a new branch for your feature:

   .. code-block:: bash

       git checkout -b feature-name

2. Make your changes and commit them:

   .. code-block:: bash

       git add .
       git commit -m "Description of changes"

3. Push to your fork:

   .. code-block:: bash

       git push origin feature-name

4. Open a Pull Request on GitHub

Guidelines
---------

- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Follow the existing code style
- Add type hints to new code
- Write docstrings for new functions/classes

Code of Conduct
-------------

Please note that ConfigBuddy has a Code of Conduct. By participating in this project, you agree to abide by its terms. 