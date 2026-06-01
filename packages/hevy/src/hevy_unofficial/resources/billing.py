from __future__ import annotations

from typing import Any

from hevy_unofficial.resources._base import BaseAPI


class BillingAPI(BaseAPI):
    """Subscriptions, Paddle, and Stripe."""

    def paddle_prices(self) -> Any:
        """GET /paddle_prices"""
        return self._request("GET", "/paddle_prices", auth=False)

    def paddle_promo_code(self, code: str) -> Any:
        """GET /paddle_promo_code_details/{code}"""
        return self._request("GET", f"/paddle_promo_code_details/{code}")

    def paddle_urls(self) -> Any:
        """GET /user/paddle_urls"""
        return self._request("GET", "/user/paddle_urls")

    def change_paddle_plan(self, payload: dict[str, Any]) -> Any:
        """POST /user/change_paddle_plan"""
        return self._request("POST", "/user/change_paddle_plan", json=payload)

    def delete_paddle_plan(self) -> Any:
        """DELETE /user/paddle_plan"""
        return self._request("DELETE", "/user/paddle_plan")

    def create_stripe_portal_session(self, payload: dict[str, Any]) -> Any:
        """POST /create_stripe_customer_portal_session"""
        return self._request("POST", "/create_stripe_customer_portal_session", json=payload)
