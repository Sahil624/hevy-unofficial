Workouts
========

Completed workouts are read from paginated user endpoints.

Paged list
----------

.. code-block:: python

   page = client.workouts.list_paged(
       username="your_username",
       limit=10,
       offset=0,
   )
   workouts = page["workouts"]

Iterator
--------

.. code-block:: python

   for workout in client.workouts.iter_paged(username="your_username", page_size=20):
       print(workout["id"], workout.get("name"))

Single workout and counts
-------------------------

.. code-block:: python

   workout = client.workouts.get(workout_id)
   count = client.workouts.count()

Calendar and metrics
--------------------

.. code-block:: python

   cal = client.workouts.calendar(year=2025, month=6)
   metrics = client.workouts.metrics(
       "total_volume",
       start_unix=1717200000,
       end_unix=1719792000,
   )

Social feed
-----------

Workout feed lives on :class:`~hevy_unofficial.resources.social.SocialAPI`:

.. code-block:: python

   feed = client.social.feed()
