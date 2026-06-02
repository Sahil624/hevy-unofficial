Hevy Unofficial
===============

Unofficial Python client for the `Hevy <https://hevy.com>`_ workout API
(``api.hevyapp.com``).

.. warning::

   This project is **not affiliated with Hevy**. The API is undocumented and may
   change without notice. Use at your own risk and respect Hevy's terms of service.

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   getting_started/installation
   getting_started/quickstart
   getting_started/authentication

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/routines
   guides/workouts
   guides/exercises

.. toctree::
   :maxdepth: 2
   :caption: API reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Project

   publishing

Features
--------

* Typed Python client built on ``httpx``
* Automatic token refresh on expiry
* Credential cache keyed by email
* Browser login via Playwright (optional ``[core]`` install to skip)
* Built-in exercise catalog extracted from hevy.com's web bundle
* Routines, workouts, social feed, coach, and billing endpoints

Quick example
-------------

.. code-block:: python

   from hevy_unofficial import HevyClient

   with HevyClient(access_token="...", refresh_token="...") as client:
       account = client.users.get_account()
       routines = client.routines.list()
       workouts = client.workouts.list_paged(
           username=account["username"],
           limit=10,
       )

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
