from __future__ import annotations

from typing import Any

from hevy_unofficial.resources._base import BaseAPI


class CoachAPI(BaseAPI):
    """Hevy Coach / trainer invites and programs."""

    def list_client_invites(self) -> Any:
        """GET /client_invites"""
        return self._request("GET", "/client_invites")

    def list_clients_coach(self) -> Any:
        """GET /clients_coach"""
        return self._request("GET", "/clients_coach")

    def get_trainer_program(self) -> Any:
        """GET /hevy_trainer/program"""
        return self._request("GET", "/hevy_trainer/program")

    def get_invite(self, invite_id: str) -> Any:
        """GET /invite/{invite_id}"""
        return self._request("GET", f"/invite/{invite_id}")

    def become_client(self, coach_username: str) -> Any:
        """GET /become_client/{coach_username}"""
        return self._request("GET", f"/become_client/{coach_username}")

    def accept_client_invite(self, invite_id: str) -> Any:
        """GET /accept_client_invite/{invite_id}"""
        return self._request("GET", f"/accept_client_invite/{invite_id}")

    def accept_client_invite_by_short_id(self, short_id: str) -> Any:
        """GET /accept_client_invite_with_short_id/{short_id}"""
        return self._request("GET", f"/accept_client_invite_with_short_id/{short_id}")

    def delete_client_invite(self, invite_id: str) -> Any:
        """DELETE /client_invites/{invite_id}"""
        return self._request("DELETE", f"/client_invites/{invite_id}")

    def delete_client_invite_by_short_id(self, short_id: str) -> Any:
        """DELETE /client_invites_with_short_id/{short_id}"""
        return self._request("DELETE", f"/client_invites_with_short_id/{short_id}")

    def join_form_metadata(self, coach_username: str) -> Any:
        """GET /coach/join_form_metadata/{coach_username}"""
        return self._request("GET", f"/coach/join_form_metadata/{coach_username}")
