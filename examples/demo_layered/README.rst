====================
Demo Layered Project
====================

A sample project for demonstrating and testing layer-enforcer.

Install and Run
===============

.. code-block:: sh

    pip install -e .
    layer-enforcer

Expected Result
===============

+------------------------------+----------------+---------------+
| Module                       | Deduced Layers | Has Conflicts |
+==============================+================+===============+
| demo_layered.domain.clean    | domain         |               |
+------------------------------+----------------+---------------+
| demo_layered.domain.indirect | domain, db     | ✔️            |
+------------------------------+----------------+---------------+
| demo_layered.domain.dirt     | domain, db     | ✔️            |
+------------------------------+----------------+---------------+
| demo_layered.db              | db             |               |
+------------------------------+----------------+---------------+
| demo_layered.web             | web            |               |
+------------------------------+----------------+---------------+
| demo_layered.indirect_web    | web            |               |
+------------------------------+----------------+---------------+
| demo_layered.indirect_db     | db             |               |
+------------------------------+----------------+---------------+
| demo_layered.dirt            | db, web        | ✔️            |
+------------------------------+----------------+---------------+
| demo_layered.ignored         | db, web        |               |
+------------------------------+----------------+---------------+
