import httpx
import pytest
import respx

from hevy_unofficial import HevyClient
from hevy_unofficial.exceptions import HevyAPIError
from hevy_unofficial.models import AuthTokens


@pytest.fixture
def client():
    with respx.mock(base_url="https://api.hevyapp.com") as router:
        c = HevyClient(
            access_token="access",
            refresh_token="refresh",
            config=__import__("hevy_unofficial.config", fromlist=["HevyConfig"]).HevyConfig(),
        )
        yield c, router


def test_get_account(client):
    c, router = client
    route = router.get("/user/account").mock(
        return_value=httpx.Response(200, json={"username": "tester"})
    )
    data = c.users.get_account()
    assert data["username"] == "tester"
    assert route.called
    assert route.calls[0].request.headers["authorization"] == "Bearer access"
    assert route.calls[0].request.headers["x-api-key"] == "shelobs_hevy_web"


def test_routine_update(client):
    c, router = client
    routine_id = "17183124-96dc-44bb-b6b8-ec0bd76cb6c5"
    body = {"routine": {"title": "Wednesday", "exercises": []}}
    route = router.put(f"/routine/{routine_id}").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    c.routines.update(routine_id, body["routine"])
    assert route.called
    assert route.calls[0].request.url.params["sendSyncEventToMobileApp"] == "true"
    assert route.calls[0].request.content


def test_sync_batch_empty(client):
    c, router = client
    route = router.post("/routines_sync_batch").mock(
        return_value=httpx.Response(200, json={"updated": [], "deleted": []})
    )
    data = c.routines.list()
    assert data["updated"] == []
    assert route.called


def test_token_refresh_on_expired(client):
    c, router = client
    router.post("/auth/refresh_token").mock(
        return_value=httpx.Response(
            200,
            json={
                "user_id": "u1",
                "access_token": "new_access",
                "refresh_token": "new_refresh",
                "expires_at": "2026-06-01T19:00:00Z",
            },
        )
    )
    router.get("/user/account").mock(
        side_effect=[
            httpx.Response(401, json={"error": "AccessTokenExpired"}),
            httpx.Response(200, json={"username": "refreshed"}),
        ]
    )
    data = c.users.get_account()
    assert data["username"] == "refreshed"
    assert c.tokens.access_token == "new_access"


def test_workouts_paged_params(client):
    c, router = client
    route = router.get("/user_workouts_paged").mock(
        return_value=httpx.Response(200, json={"workouts": []})
    )
    c.workouts.list_paged(username="alice", limit=3, offset=4)
    assert route.calls[0].request.url.params["username"] == "alice"
    assert route.calls[0].request.url.params["limit"] == "3"
    assert route.calls[0].request.url.params["offset"] == "4"


def test_api_error(client):
    c, router = client
    router.get("/workout_count").mock(return_value=httpx.Response(500, json={"error": "x"}))
    with pytest.raises(HevyAPIError) as exc:
        c.workouts.count()
    assert exc.value.status_code == 500


def test_login_sets_tokens():
    with respx.mock(base_url="https://api.hevyapp.com") as router:
        router.post("/login").mock(
            return_value=httpx.Response(
                200,
                json={
                    "user_id": "u1",
                    "access_token": "a",
                    "refresh_token": "r",
                    "expires_at": "2026-06-01T19:00:00Z",
                },
            )
        )
        with HevyClient() as c:
            tokens = c.auth.login(
                "user@example.com",
                "secret",
                recaptcha_token="token",
            )
            assert isinstance(tokens, AuthTokens)
            assert c.tokens.access_token == "a"
