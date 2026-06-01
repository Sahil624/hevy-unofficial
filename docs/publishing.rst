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

GitHub Pages
------------

On push to ``main``, after tests pass, the workflow ``.github/workflows/ci.yml``:

1. Installs the package and Sphinx dependencies
2. Sets ``DOCS_BASE_URL`` to ``https://<owner>.github.io/<repo>/``
3. Builds HTML to ``docs/_build/html``
4. Deploys via `GitHub Pages <https://pages.github.com/>`_

Enable Pages in the repository settings:

* **Source**: GitHub Actions

After the first successful deploy, docs are available at:

``https://<github-owner>.github.io/<repository-name>/``

Replace ``hevy-unofficial`` placeholders in ``docs/conf.py`` ``source_repository``
URLs if your fork uses a different remote.

PyPI releases
-------------

On push of a version tag (``v*``), ``.github/workflows/pypi.yml``:

1. Checks the tag (without ``v``) matches ``version`` in ``packages/hevy/pyproject.toml``
2. Builds sdist and wheel
3. Publishes to PyPI

Example:

.. code-block:: bash

   git tag v0.1.0
   git push origin v0.1.0

Configure `PyPI trusted publishing <https://docs.pypi.org/trusted-publishers/>`_
for this repository and workflow, or add a ``PYPI_API_TOKEN`` secret.
