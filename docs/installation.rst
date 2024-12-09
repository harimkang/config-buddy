Installation
============

ConfigBuddy can be installed via pip:

.. code-block:: bash

    pip install configbuddy

Requirements
-----------

ConfigBuddy requires Python 3.8 or later. The following dependencies will be automatically installed:

- PyYAML
- rich
- jsonschema

Development Installation
----------------------

To install ConfigBuddy for development:

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/harimkang/configbuddy.git
       cd configbuddy

2. Create a virtual environment (optional but recommended):

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies:

   .. code-block:: bash

       pip install -e "."
