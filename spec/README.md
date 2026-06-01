# API contract

Shared endpoint notes for the Python client.

- **Base URL:** `https://api.hevyapp.com`
- **Web API key:** `shelobs_hevy_web` (`x-api-key` header)
- **Platform:** `web` (`hevy-platform` header)
- **Auth:** `Authorization: Bearer {access_token}` on authenticated routes
- **Refresh:** `POST /auth/refresh_token` with body `{"refresh_token": "..."}` and
  `Authorization: Bearer {access_token}`

See [`routes.md`](routes.md) for route summaries and [`packages/hevy`](../packages/hevy) for the client implementation.
