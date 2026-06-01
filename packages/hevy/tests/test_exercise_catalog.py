import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
import respx

from hevy_unofficial.exercise_catalog import (
    CatalogMeta,
    ExerciseCatalogStore,
    discover_app_js_url,
    parse_exercises_from_app_js,
)

SAMPLE_SEGMENT = (
    '{"id":"99D5F10E","title":"Ab Wheel","priority":0,"muscle_group":"abdominals",'
    '"other_muscles":[],"exercise_type":"reps_only","equipment_category":"other",'
    '"url":"https://cdn.example/video.mp4","media_type":"video",'
    '"thumbnail_url":"https://cdn.example/thumb.jpg","is_custom":false}'
)


def test_parse_single_exercise():
    exercises = parse_exercises_from_app_js(SAMPLE_SEGMENT)
    assert len(exercises) == 1
    assert exercises[0]["id"] == "99D5F10E"
    assert exercises[0]["title"] == "Ab Wheel"
    assert exercises[0]["muscle_group"] == "abdominals"


def test_discover_app_js_url():
    html = '<script src="/_next/static/chunks/pages/_app-7d6ac0edddbd363a.js"></script>'
    url = discover_app_js_url(html, base_url="https://hevy.com")
    assert url.endswith("_app-7d6ac0edddbd363a.js")


def test_cache_uses_fresh_file_without_network(tmp_path):
    store = ExerciseCatalogStore(tmp_path)
    exercises = [{"id": "AAAAAAAA", "title": "Test", "muscle_group": "chest"}]
    meta = CatalogMeta(
        etag='"abc"',
        source_url="https://hevy.com/_next/static/chunks/pages/_app-deadbeef.js",
        fetched_at=datetime.now(timezone.utc).isoformat(),
        parsed_at=datetime.now(timezone.utc).isoformat(),
        exercise_count=1,
    )
    store.save(meta, exercises)

    result = store.fetch_and_update(refresh=False, max_age=timedelta(days=7))
    assert result == exercises


@respx.mock
def test_etag_304_keeps_cache(tmp_path):
    store = ExerciseCatalogStore(tmp_path)
    app_url = "https://hevy.com/_next/static/chunks/pages/_app-deadbeef.js"
    exercises = parse_exercises_from_app_js(SAMPLE_SEGMENT)
    meta = CatalogMeta(
        etag='"etag-1"',
        source_url=app_url,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        parsed_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        exercise_count=len(exercises),
    )
    store.save(meta, exercises)

    home_html = f'<script src="{app_url}"></script>'
    respx.get("https://hevy.com/").mock(return_value=httpx.Response(200, text=home_html))
    respx.get(app_url).mock(return_value=httpx.Response(304))

    result = store.fetch_and_update(refresh=True)
    assert len(result) == 1
    assert result[0]["id"] == "99D5F10E"


@respx.mock
def test_new_etag_triggers_reparse(tmp_path):
    store = ExerciseCatalogStore(tmp_path)
    app_url = "https://hevy.com/_next/static/chunks/pages/_app-deadbeef.js"
    old_exercises = [{"id": "OLDID001", "title": "Old", "muscle_group": "chest"}]
    meta = CatalogMeta(
        etag='"etag-old"',
        source_url=app_url,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        parsed_at=datetime.now(timezone.utc).isoformat(),
        exercise_count=1,
    )
    store.save(meta, old_exercises)

    js_body = SAMPLE_SEGMENT
    home_html = f'<script src="{app_url}"></script>'
    respx.get("https://hevy.com/").mock(return_value=httpx.Response(200, text=home_html))
    respx.get(app_url).mock(
        return_value=httpx.Response(200, text=js_body, headers={"etag": '"etag-new"'})
    )

    result = store.fetch_and_update(refresh=True)
    assert result[0]["id"] == "99D5F10E"

    saved = json.loads(store.catalog_path.read_text())
    assert saved["meta"]["etag"] == '"etag-new"'
    assert saved["meta"]["exercise_count"] == 1
