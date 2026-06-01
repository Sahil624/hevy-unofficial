Quick start
===========

Create a client
---------------

The web app uses ``Authorization: Bearer`` tokens. Obtain ``access_token`` and
``refresh_token`` from browser DevTools after logging in at `hevy.com
<https://hevy.com>`_, or use :doc:`authentication` helpers.

.. code-block:: python

   from hevy_unofficial import HevyClient

   with HevyClient(
       access_token="YOUR_ACCESS_TOKEN",
       refresh_token="YOUR_REFRESH_TOKEN",
   ) as client:
       account = client.users.get_account()
       print(account["username"])

       routines = client.routines.list()
       print(len(routines.get("updated", [])), "routines")

Account and workouts
--------------------

.. code-block:: python

   username = client.users.get_account()["username"]

   page = client.workouts.list_paged(username=username, limit=10, offset=0)
   for workout in page.get("workouts", []):
       print(workout["name"], workout.get("start_time"))

Iterate all workouts
--------------------

.. code-block:: python

   for workout in client.workouts.iter_paged(username=username, page_size=10):
       print(workout["id"], workout["name"])

Environment variables
---------------------

Optional overrides (see :class:`~hevy_unofficial.config.HevyConfig`):

.. list-table::
   :header-rows: 1

   * - Variable
     - Default
   * - ``HEVY_BASE_URL``
     - ``https://api.hevyapp.com``
   * - ``HEVY_API_KEY``
     - ``shelobs_hevy_web`` (web client key)
   * - ``HEVY_PLATFORM``
     - ``web``

Errors
------

API failures raise :class:`~hevy_unofficial.exceptions.HevyAPIError`. Auth and
refresh problems raise :class:`~hevy_unofficial.exceptions.HevyAuthError`.

.. code-block:: python

   from hevy_unofficial.exceptions import HevyAPIError

   try:
       client.workouts.get("invalid-id")
   except HevyAPIError as exc:
       print(exc.status_code, exc.body)
