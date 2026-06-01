from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class HevyConfig:
    """Client configuration."""

    base_url: str = "https://api.hevyapp.com"
    api_key: str = "shelobs_hevy_web"
    platform: str = "web"
    user_agent: str = (
        "Mozilla/5.0 (compatible; hevy-unofficial/0.1.0)"
    )
    origin: str = "https://hevy.com"
    referer: str = "https://hevy.com/"
    accept_language: str = "en-US,en;q=0.8"
    timeout: float = 30.0
    auto_refresh: bool = True
    token_refresh_throttle_seconds: float = 5.0

    @classmethod
    def from_env(cls) -> HevyConfig:
        return cls(
            base_url=os.getenv("HEVY_BASE_URL", cls.base_url),
            api_key=os.getenv("HEVY_API_KEY", cls.api_key),
            platform=os.getenv("HEVY_PLATFORM", cls.platform),
        )
