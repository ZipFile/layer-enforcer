==============
Layer Enforcer
==============

Layer Enforcer is a tool for linting your imports within the project.

The tool was designed to help maintain following order of things:

* Dependencies always flow towards root of the tree. Often this is ``domain``
  layer.
* Dependencies may skip layers, as long as they flow in same direction.
  For instance, your ``web`` layer may import use cases from ``domain`` layer.
* Infer layer from imports or module names. Say, if you import ``fastapi``
  anywhere on the chain, the module is assigned to ``web`` layer, or maybe you
  want ``models`` to always be ``db`` layer.
* Flexible layer structure. Preferably defined via config file.
* Code is packaged by component. I.e. single component may contain code from
  the different layers.

Be warned, since this might not the best fit for you.

Algorithm
=========

First pass: Match modules to layers. Report conflict if single module match
more than one layer.

Second pass: For each module, iterate through all the imported modules.
If current module has no assigned layer, assign first found layer within list
of imported modules. If current module has an assigned layer, report conflict
if import is not allowed.

Installation
============

.. code-block:: sh

    pip install layer-enforcer

For Development
---------------

.. code-block:: sh

    pip install -e .[test,lint]

Usage
=====

.. code-block:: sh

    layer-enforcer myproject myotherproject --layers layers.yaml


layers.yaml
-----------

An example of clean-architecture-ish layer layout for typical web app:

.. code-block:: yaml

    name: domain
    submodules: ["entities", "use_cases"]
    layers:
    - name: service
      submodules: ["services"]
      layers:
      - name: infrastructure
        imports: ["stripe", "requests", "passlib"]
        layers:
        - name: db
          imports: ["sqlalchemy", "psycopg2", "alembic"]
          submodules: ["models", "memory", "database"]
        - name: web
          imports: ["fastapi", "jose"]
          submodules: ["views", "schemas"]
        - name: tasks
          imports: ["celery"]
          submodules: ["tasks"]
