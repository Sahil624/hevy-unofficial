Exercises
=========

Custom exercises
----------------

User-created exercises use the API:

.. code-block:: python

   custom = client.exercises.list_custom_templates()
   client.exercises.create_custom_template({...})
   client.exercises.update_custom_template({...})
   client.exercises.delete_custom_template(template_id)

Built-in catalog (~429 exercises)
---------------------------------

Hevy's web UI does **not** load the full library from a list API. Exercises are
embedded in ``/_next/static/chunks/pages/_app-<hash>.js``.

This package extracts them into a local JSON cache:

.. code-block:: python

   catalog = client.exercises.list_catalog()
   for ex in catalog:
       print(ex["id"], ex["title"])

Behavior:

* Default cache: ``~/.config/hevy-unofficial/exercise_catalog.json`` (or next to
  your credential store if configured)
* **ETag** check when cache is older than 7 days (configurable)
* Pass ``refresh=True`` to force re-download and re-parse

.. code-block:: python

   catalog = client.exercises.list_catalog(refresh=True)
   catalog = client.exercises.list_catalog(max_age=timedelta(days=1))

Offline parsing
---------------

If you have saved the hevy.com ``_app`` bundle locally:

.. code-block:: python

   catalog = client.exercises.parse_catalog_from_js("/path/to/_app-xxxxx.js")

This writes the same ``exercise_catalog.json`` cache used by :meth:`~hevy_unofficial.resources.exercises.ExercisesAPI.list_catalog`.
