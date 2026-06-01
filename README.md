# hevy-unofficial

Unofficial [Hevy](https://hevy.com) API client for Python (`api.hevyapp.com`).

| Component | Path | Description |
|-----------|------|-------------|
| **hevy-unofficial** (PyPI) | [`packages/hevy`](packages/hevy) | Python client |
| API contract notes | [`spec`](spec) | Endpoint reference |

## Python client

```bash
pip install hevy-unofficial
# or from source:
pip install -e "packages/hevy[dev]"
```

```python
from hevy_unofficial import HevyClient

with HevyClient(access_token="...", refresh_token="...") as client:
    print(client.users.get_account())
    print(client.routines.list())
```

See [packages/hevy/README.md](packages/hevy/README.md) for package details.

## Documentation

Sphinx docs live in [`docs/`](docs/). After enabling [GitHub Pages](https://pages.github.com/) (source: **GitHub Actions**), they publish to:

`https://<your-github-user>.github.io/<repo-name>/`

Build locally:

```bash
pip install -e packages/hevy && pip install -r docs/requirements.txt
make -C docs html
# open docs/_build/html/index.html
```

## License

MIT — see [packages/hevy/LICENSE](packages/hevy/LICENSE).
