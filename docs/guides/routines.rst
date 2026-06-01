Routines
========

Routines are training templates (exercises, sets, rest timers). The web app syncs
them via batch endpoints.

List routines
-------------

.. code-block:: python

   data = client.routines.list()
   # data["updated"] — routine objects
   # data["deleted"] — IDs removed since last sync (if applicable)

``list()`` calls ``POST /routines_sync_batch`` with ``{}`` for a full sync.

Create, update, delete
----------------------

.. code-block:: python

   created = client.routines.create({
       "title": "Push Day",
       "exercises": [...],
   })

   client.routines.update(routine_id, {"title": "Push A"})
   client.routines.delete(routine_id)

Folders and locations
---------------------

.. code-block:: python

   client.routines.update_locations([...])
   client.routines.create_folder({"name": "Hypertrophy"})
   client.routines.update_folder(folder_id, {"name": "Strength"})
   client.routines.delete_folder(folder_id)

Mobile sync flag
----------------

Mutations append ``sendSyncEventToMobileApp=true`` so the mobile app receives
sync events, matching the web client.
