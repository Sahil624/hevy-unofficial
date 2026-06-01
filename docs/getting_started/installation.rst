Installation
==============

From PyPI
---------

.. code-block:: bash

   pip install hevy-unofficial

From source
-----------

.. code-block:: bash

   git clone https://github.com/Sahil624/hevy-unofficial.git
   cd <repo>
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -e "packages/hevy[dev]"

Requirements
------------

* Python 3.10 or newer
* `httpx <https://www.python-httpx.org/>`_
* `pydantic <https://docs.pydantic.dev/>`_ v2

Optional: documentation build tools
------------------------------------

.. code-block:: bash

   pip install -r docs/requirements.txt
