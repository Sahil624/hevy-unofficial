Building and publishing docs
=============================

Local build
-----------

.. code-block:: bash

   pip install -r docs/requirements.txt
   pip install -e packages/hevy
   make -C docs html

Open ``docs/_build/html/index.html`` in a browser.

Live reload
-----------

.. code-block:: bash

   pip install sphinx-autobuild
   make -C docs livehtml

Continuous integration
----------------------

On every push to ``main`` and on pull requests, ``.github/workflows/ci.yml``:

1. Runs unit tests
2. **Builds** Sphinx HTML (verification only — does not deploy)

Release (PyPI + GitHub Pages)
-----------------------------

On push of a version tag (``v*``), ``.github/workflows/pypi.yml`` runs in order:

1. **Tests** — same pytest suite as CI
2. **PyPI** — tag must match ``version`` in ``packages/hevy/pyproject.toml``; uploads wheel/sdist
3. **Docs** — builds Sphinx HTML (only after PyPI succeeds)
4. **GitHub Pages** — deploys that build

Example:

.. code-block:: bash

   # bump version in packages/hevy/pyproject.toml first
   git tag v0.1.0
   git push origin v0.1.0

Enable Pages in the repository settings:

* **Source**: GitHub Actions

After the first successful release deploy, docs are available at:

``https://<github-owner>.github.io/<repository-name>/``

Replace ``hevy-unofficial`` placeholders in ``docs/conf.py`` ``source_repository``
URLs if your fork uses a different remote.

PyPI trusted publishing
~~~~~~~~~~~~~~~~~~~~~~~

Configure `PyPI trusted publishing <https://docs.pypi.org/trusted-publishers/>`_
for workflow file **`pypi.yml`** (not ``pypi.yaml``), environment ``pypi``, and
repository ``Sahil624/hevy-unofficial`` (adjust if forked).

Or add repository secret ``PYPI_API_TOKEN`` for token-based upload.
