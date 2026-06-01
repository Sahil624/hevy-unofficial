Authentication
================

Token model
-----------

``POST /login`` returns:

* ``user_id``
* ``access_token`` (short-lived, ~15 minutes in web captures)
* ``refresh_token``
* ``expires_at``

Authenticated requests send::

   Authorization: Bearer <access_token>
   x-api-key: shelobs_hevy_web
   hevy-platform: web
   x-client-time: <unix seconds>

The client refreshes automatically when the API returns ``401`` with
``AccessTokenExpired``.

Programmatic login
------------------

Web login requires a **reCAPTCHA** token, so automated password login is difficult
without browser automation.

.. code-block:: python

   tokens = client.auth.login(
       email_or_username="you@example.com",
       password="your-password",
       recaptcha_token="...",  # from browser session
   )

Refresh and logout
------------------

.. code-block:: python

   client.auth.refresh()   # uses stored refresh_token
   client.auth.logout()    # DELETE /auth/session

Credential cache
----------------

Cache tokens by email; refreshed tokens are written back automatically.

.. code-block:: python

   from hevy_unofficial import CredentialStore, prompt_client

   store = CredentialStore()  # ~/.config/hevy-unofficial/credentials.json

   with prompt_client(store=store) as client:
       account = client.users.get_account()

First run prompts for email and tokens. Later runs reuse the cache unless you
pass ``force_prompt=True``.

Cache files (mode ``0600`` where supported):

* ``credentials.json`` — tokens per email
* ``exercise_catalog.json`` — built-in exercise library (see :doc:`../guides/exercises`)
