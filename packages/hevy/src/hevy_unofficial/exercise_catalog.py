from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from hevy_unofficial.credentials import default_cache_dir

HEVY_HOME_URL = "https://hevy.com/"
APP_JS_PATH_RE = re.compile(
    r"(/_next/static/chunks/pages/_app-[a-f0-9]+\.js)",
    re.IGNORECASE,
)
DEFAULT_STALE_AFTER = timedelta(days=7)
CATALOG_FILENAME = "exercise_catalog.json"


@dataclass
class CatalogMeta:
    etag: str | None
    source_url: str
    fetched_at: str
    parsed_at: str
    exercise_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "etag": self.etag,
            "source_url": self.source_url,
            "fetched_at": self.fetched_at,
            "parsed_at": self.parsed_at,
            "exercise_count": self.exercise_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CatalogMeta:
        return cls(
            etag=data.get("etag"),
            source_url=data["source_url"],
            fetched_at=data["fetched_at"],
            parsed_at=data["parsed_at"],
            exercise_count=int(data.get("exercise_count", 0)),
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def discover_app_js_url(home_html: str, *, base_url: str = HEVY_HOME_URL) -> str:
    """Find the hashed ``_app-….js`` chunk URL from the Hevy homepage HTML."""
    match = APP_JS_PATH_RE.search(home_html)
    if not match:
        raise ValueError("Could not find _app-*.js chunk path on hevy.com homepage")
    path = match.group(1)
    return f"{base_url.rstrip('/')}{path}"


def parse_exercises_from_app_js(js_text: str) -> list[dict[str, Any]]:
    """
    Extract built-in exercise templates embedded in the Next.js ``_app`` bundle.

    The bundle is JavaScript, not strict JSON (escaped newlines in strings), so we
    split on exercise boundaries and pull fields with regex.
    """
    if '},{"id":"' in js_text:
        parts = js_text.split('},{"id":"')
    elif re.search(r'\{"id":"[A-F0-9]{8}"', js_text):
        parts = [js_text]
    else:
        return []
    exercises: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}

    for index, part in enumerate(parts):
        segment = part if index == 0 else '{"id":"' + part

        exercise_id = _regex_field(segment, "id", r'"id":"([A-F0-9]{8})"')
        title = _regex_field(segment, "title")
        muscle_group = _regex_field(segment, "muscle_group")
        if not exercise_id or not title or not muscle_group:
            continue

        exercise = {
            "id": exercise_id,
            "title": title,
            "muscle_group": muscle_group,
            "equipment_category": _regex_field(segment, "equipment_category"),
            "exercise_type": _regex_field(segment, "exercise_type"),
            "url": _regex_field(segment, "url"),
            "thumbnail_url": _regex_field(segment, "thumbnail_url"),
            "media_type": _regex_field(segment, "media_type"),
            "priority": _regex_int(segment, "priority"),
            "is_custom": _regex_bool(segment, "is_custom"),
            "other_muscles": _regex_array(segment, "other_muscles") or [],
        }
        seen[exercise_id] = exercise

    exercises.extend(seen.values())
    exercises.sort(key=lambda item: item.get("title", "").lower())
    return exercises


def _regex_field(segment: str, name: str, pattern: str | None = None) -> str | None:
    pat = pattern or rf'"{name}":"((?:[^"\\]|\\.)*)"'
    match = re.search(pat, segment)
    return match.group(1) if match else None


def _regex_bool(segment: str, name: str) -> bool | None:
    match = re.search(rf'"{name}":(true|false)', segment)
    if not match:
        return None
    return match.group(1) == "true"


def _regex_int(segment: str, name: str) -> int | None:
    match = re.search(rf'"{name}":(-?\d+)', segment)
    return int(match.group(1)) if match else None


def _regex_array(segment: str, name: str) -> list[Any] | None:
    match = re.search(rf'"{name}":(\[[^\]]*\])', segment)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, list) else None


class ExerciseCatalogStore:
    """Local cache for the built-in exercise catalog (same directory as credentials)."""

    def __init__(self, cache_dir: Path | str | None = None) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else default_cache_dir()
        self.catalog_path = self.cache_dir / CATALOG_FILENAME

    def load(self) -> tuple[CatalogMeta | None, list[dict[str, Any]]]:
        if not self.catalog_path.is_file():
            return None, []
        data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        meta = CatalogMeta.from_dict(data["meta"]) if data.get("meta") else None
        exercises = data.get("exercises") or []
        return meta, exercises

    def save(self, meta: CatalogMeta, exercises: list[dict[str, Any]]) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "meta": meta.to_dict(),
            "exercises": exercises,
        }
        self.catalog_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        try:
            import os

            os.chmod(self.catalog_path, 0o600)
        except OSError:
            pass

    def is_stale(self, meta: CatalogMeta | None, *, max_age: timedelta = DEFAULT_STALE_AFTER) -> bool:
        if meta is None:
            return True
        try:
            parsed_at = _parse_iso(meta.parsed_at)
        except ValueError:
            return True
        return datetime.now(timezone.utc) - parsed_at > max_age

    def fetch_and_update(
        self,
        *,
        refresh: bool = False,
        max_age: timedelta = DEFAULT_STALE_AFTER,
        user_agent: str | None = None,
        timeout: float = 60.0,
    ) -> list[dict[str, Any]]:
        """
        Return the exercise catalog, refreshing from hevy.com when needed.

        - ``refresh=False``: use cache if younger than ``max_age`` (default 7 days).
        - ``refresh=True``: always check remote ``_app`` JS ETag; re-download and
          re-parse only when the ETag changes (or cache is missing).
        """
        meta, exercises = self.load()

        if not refresh and exercises and not self.is_stale(meta, max_age=max_age):
            return exercises

        headers = {"User-Agent": user_agent or "hevy-unofficial/0.1.0"}
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as http:
            home = http.get(HEVY_HOME_URL)
            home.raise_for_status()
            app_js_url = discover_app_js_url(home.text)

            request_headers = {}
            if meta and meta.etag and meta.source_url == app_js_url:
                request_headers["If-None-Match"] = meta.etag

            app_response = http.get(app_js_url, headers=request_headers)
            if app_response.status_code == 304 and exercises:
                return exercises
            app_response.raise_for_status()

            new_etag = app_response.headers.get("etag")
            if (
                not refresh
                and exercises
                and meta
                and meta.source_url == app_js_url
                and new_etag
                and meta.etag == new_etag
            ):
                return exercises

            parsed = parse_exercises_from_app_js(app_response.text)
            new_meta = CatalogMeta(
                etag=new_etag,
                source_url=app_js_url,
                fetched_at=_utc_now(),
                parsed_at=_utc_now(),
                exercise_count=len(parsed),
            )
            self.save(new_meta, parsed)
            return parsed

    def parse_app_js_from_har(self, har_path: Path | str) -> list[dict[str, Any]]:
        """Extract ``_app-*.js`` from a HAR capture and parse exercises."""
        har_path = Path(har_path)
        har = json.loads(har_path.read_text(encoding="utf-8"))
        for entry in har.get("log", {}).get("entries", []):
            url = entry.get("request", {}).get("url", "")
            if "/_next/static/chunks/pages/_app-" in url and url.endswith(".js"):
                text = entry.get("response", {}).get("content", {}).get("text") or ""
                if text:
                    exercises = parse_exercises_from_app_js(text)
                    meta = CatalogMeta(
                        etag=None,
                        source_url=url,
                        fetched_at=_utc_now(),
                        parsed_at=_utc_now(),
                        exercise_count=len(exercises),
                    )
                    self.save(meta, exercises)
                    return exercises
        raise ValueError(f"No _app-*.js response found in HAR: {har_path}")

    def parse_local_js_file(self, js_path: Path | str) -> list[dict[str, Any]]:
        """Parse exercises from a local ``_app-….js`` file (offline / HAR export)."""
        text = Path(js_path).read_text(encoding="utf-8", errors="replace")
        exercises = parse_exercises_from_app_js(text)
        meta = CatalogMeta(
            etag=None,
            source_url=str(Path(js_path).resolve()),
            fetched_at=_utc_now(),
            parsed_at=_utc_now(),
            exercise_count=len(exercises),
        )
        self.save(meta, exercises)
        return exercises
