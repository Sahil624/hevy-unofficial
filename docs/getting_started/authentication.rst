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

Browser login (recommended)
---------------------------

When Playwright is installed and you have a graphical session, the client can
open hevy.com and read the ``auth2.0-token`` cookie after you log in (or if you
are already logged in).

Install (full package, includes Playwright):

.. code-block:: bash

   pip install hevy-unofficial
   playwright install chromium

Minimal install without browser automation:

.. code-block:: bash

   pip install 'hevy-unofficial[core]'

.. code-block:: python

   from hevy_unofficial import capture_tokens_via_browser, CredentialStore, login_via_browser

   store = CredentialStore()
   tokens, email = login_via_browser(email="you@example.com", store=store)

   # Or only capture tokens (no cache write):
   tokens = capture_tokens_via_browser()

:func:`~hevy_unofficial.credentials.prompt_client` tries browser login automatically
when no cached credentials exist, then falls back to typing tokens on stdin.

.. code-block:: python

   from hevy_unofficial import prompt_client

   with prompt_client(use_browser=True) as client:
       account = client.users.get_account()

Headless / CI environments
~~~~~~~~~~~~~~~~~~~~~~~~~~

On servers without a display (or when ``CI=true``), browser login is skipped unless
you set ``HEVY_FORCE_BROWSER=1``. Use ``use_browser=False`` or paste tokens manually.

Environment variables:

* ``HEVY_FORCE_BROWSER=1`` — attempt browser login even in CI (usually fails without a display)
* ``HEVY_SKIP_BROWSER=1`` — never use browser login
* ``CI`` / ``GITHUB_ACTIONS`` — treated as headless

Programmatic password login
---------------------------

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

First run uses browser login when available, otherwise prompts for tokens.
Later runs reuse the cache unless you pass ``force_prompt=True``.

Cache files (mode ``0600`` where supported):

* ``credentials.json`` — tokens per email
* ``exercise_catalog.json`` — built-in exercise library (see :doc:`../guides/exercises`)
