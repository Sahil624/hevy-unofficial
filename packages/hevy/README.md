# hevy-unofficial

Unofficial Python client for the [Hevy](https://hevy.com) workout API (`api.hevyapp.com`).

> **Disclaimer:** Not affiliated with Hevy. The API is undocumented and may change.
> Use at your own risk and respect Hevy's terms of service.

## Install

```bash
pip install hevy-unofficial
playwright install chromium
```

Without browser automation (lighter install):

```bash
pip install 'hevy-unofficial[core]'
```

Development install from source:

```bash
pip install -e "packages/hevy[dev]"
# CI / headless dev without Playwright:
pip install -e "packages/hevy[dev,core]"
```

## Quick start

Use tokens from a browser session or from `POST /login` (login requires reCAPTCHA on web):

```python
from hevy_unofficial import HevyClient

with HevyClient(
    access_token="YOUR_ACCESS_TOKEN",
    refresh_token="YOUR_REFRESH_TOKEN",
) as client:
    account = client.users.get_account()
    print(account["username"])

    routines = client.routines.list()
    workouts = client.workouts.list_paged(username=account["username"], limit=10)
```

Environment variables (optional):

- `HEVY_BASE_URL` — default `https://api.hevyapp.com`
- `HEVY_API_KEY` — default `shelobs_hevy_web` (web client key)
- `HEVY_PLATFORM` — default `web`

### Browser login

Opens hevy.com and reads the `auth2.0-token` cookie (login if needed):

```python
from hevy_unofficial import CredentialStore, login_via_browser, prompt_client

store = CredentialStore()
tokens, email = login_via_browser(email="you@example.com", store=store)

# prompt_client tries browser login when Playwright + display are available
with prompt_client(store=store) as client:
    ...
```

On headless servers (CI, no `DISPLAY`), browser login is skipped automatically.
Set `HEVY_FORCE_BROWSER=1` to override, or `use_browser=False` for manual tokens.

### Credential cache

Tokens can be cached by email and updated automatically after refresh:

```python
from hevy_unofficial import CredentialStore, prompt_client

store = CredentialStore()  # ~/.config/hevy-unofficial/credentials.json
with prompt_client(store=store) as client:
    ...
```

On first run, browser login is attempted when available; otherwise you enter tokens.
Later runs reuse the cache.

## API surface

The client mirrors the web app's HTTP API:

| Attribute | Domain |
|-----------|--------|
| `client.auth` | Login, signup, refresh, logout, passwords |
| `client.users` | Account, profile, preferences, API keys |
| `client.routines` | Routines, folders, sync batch, reorder |
| `client.workouts` | History, comments, likes, metrics, calendar |
| `client.exercises` | Built-in catalog (cached), custom templates, history |
| `client.social` | Feed, follow, followers |
| `client.coach` | Coach invites and trainer program |
| `client.billing` | Paddle / Stripe subscription helpers |
| `client.misc` | Webhooks, OAuth, uploads, feedback |

### Exercise catalog

Built-in templates are extracted from hevy.com's `_app-*.js` bundle (not the REST API):

```python
# Cached for 7 days in ~/.config/hevy-unofficial/exercise_catalog.json
exercises = client.exercises.list_catalog()

# Force ETag check / re-download if the bundle changed
exercises = client.exercises.list_catalog(refresh=True)
```

Offline extraction from a saved JS file:

```python
client.exercises.parse_catalog_from_js("path/to/_app-xxx.js")
```

### Routines example

```python
# List all routines (sync)
data = client.routines.list()

# Create
created = client.routines.create({
    "title": "Push Day",
    "exercises": [],
    "folder_id": None,
    "index": 0,
    "program_id": None,
    "notes": None,
    "coach_force_rpe_enabled": False,
})
routine_id = created["routineId"]

# Update
client.routines.update(routine_id, {
    "title": "Push Day A",
    "exercises": [...],
    "folder_id": None,
    "index": 0,
    "program_id": None,
    "notes": None,
    "coach_force_rpe_enabled": False,
})

# Delete
client.routines.delete(routine_id)
```

## Publishing to PyPI

Push a version tag (must match ``version`` in ``pyproject.toml``):

```bash
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions builds the wheel/sdist and publishes to PyPI (requires a
``PYPI_API_TOKEN`` repository secret or PyPI trusted publishing for this repo).

Manual upload:

```bash
cd packages/hevy
pip install build twine
python -m build
twine upload dist/*
```

## Tests

```bash
cd packages/hevy
pytest
```
