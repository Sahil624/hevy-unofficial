"""Unofficial Python client for api.hevyapp.com."""

from hevy_unofficial.client import HevyClient
from hevy_unofficial.config import HevyConfig
from hevy_unofficial.exceptions import (
    HevyAPIError,
    HevyAuthError,
    HevyError,
    HevyRateLimitError,
)
from hevy_unofficial.credentials import CredentialStore, prompt_client
from hevy_unofficial.exercise_catalog import ExerciseCatalogStore, parse_exercises_from_app_js
from hevy_unofficial.models import AuthTokens

__all__ = [
    "AuthTokens",
    "CredentialStore",
    "ExerciseCatalogStore",
    "HevyAPIError",
    "HevyAuthError",
    "HevyClient",
    "HevyConfig",
    "HevyError",
    "HevyRateLimitError",
    "__version__",
    "parse_exercises_from_app_js",
    "prompt_client",
]
__version__ = "0.1.0"
