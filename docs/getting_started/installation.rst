Installation
==============

From PyPI
---------

Full install (HTTP client + browser login):

.. code-block:: bash

   pip install hevy-unofficial
   playwright install chromium

Minimal install (skip browser automation):

.. code-block:: bash

   pip install 'hevy-unofficial[core]'

From source
-----------

.. code-block:: bash

   git clone https://github.com/Sahil624/hevy-unofficial.git
   cd hevy-unofficial
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -e "packages/hevy[dev]"

Development without Playwright:

.. code-block:: bash

   pip install -e "packages/hevy[dev,core]"

Requirements
------------

* Python 3.10 or newer
* `httpx <https://www.python-httpx.org/>`_
* `pydantic <https://docs.pydantic.dev/>`_ v2
* `Playwright <https://playwright.dev/python/>`_ (default install; run ``playwright install chromium``)

Optional: documentation build tools
------------------------------------

.. code-block:: bash

   pip install -r docs/requirements.txt
