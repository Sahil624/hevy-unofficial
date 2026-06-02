from __future__ import annotations

from typing import Any


class HevyError(Exception):
    """Base error for the hevy-unofficial package."""


class HevyAPIError(HevyError):
  """HTTP API returned an error status."""

  def __init__(
      self,
      message: str,
      *,
      status_code: int,
      method: str,
      path: str,
      body: Any = None,
  ) -> None:
      super().__init__(message)
      self.status_code = status_code
      self.method = method
      self.path = path
      self.body = body


class HevyAuthError(HevyAPIError):
    """Authentication or token refresh failed."""


class HevyRateLimitError(HevyAPIError):
    """Rate limit exceeded (HTTP 429)."""


class HevyBrowserError(HevyError):
    """Browser-based login or auth cookie extraction failed."""
