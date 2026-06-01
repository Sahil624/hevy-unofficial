# Hevy API routes (unofficial)

Extracted from the Hevy web app (`_app` bundle) and HAR captures. Implemented in `packages/hevy`.

## Auth

| Method | Path |
|--------|------|
| POST | `/login` |
| POST | `/login_google_web` |
| POST | `/login_apple_web` |
| POST | `/auth/refresh_token` |
| POST | `/auth/migrate` |
| DELETE | `/auth/session` |
| POST | `/signup`, `/sign_up_google_web`, `/signup_apple_web`, `/signup_with_verified_email` |
| POST | `/send_signup_verification_email`, `/recover_password`, `/update_password` |
| PUT | `/update_password_with_password` |
| POST | `/link_with_gympass` |

## Routines

| Method | Path |
|--------|------|
| POST | `/routines_sync_batch` |
| GET | `/routine/{id}`, `/routine_with_short_id/{shortId}` |
| POST | `/routine?sendSyncEventToMobileApp=true` |
| PUT | `/routine/{id}?sendSyncEventToMobileApp=true` |
| DELETE | `/routine/{id}?sendSyncEventToMobileApp=true` |
| POST | `/routine_copy` |
| GET | `/routine_folders` |
| POST | `/routine_folder`, PUT `/routine_folder`, DELETE `/routine_folder/{id}` |
| PUT | `/routine_locations`, `/routine_folder_order` |
| GET | `/shareable_folder/{id}` |

## Workouts

| Method | Path |
|--------|------|
| GET | `/user_workouts_paged`, `/workout/{id}`, `/workouts_batch/{id}` |
| GET | `/workout_count`, `/user_calendar_workouts/{year}/{month}` |
| GET | `/user_workout_metrics/{metric}/{start}/{end}` |
| GET | `/user_workout_images/{username}/{page}` |
| GET/POST/DELETE | workout comments & likes |

See Python resource modules for the full list.
