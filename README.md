# CHATAIA-run-local-chatbot-with-ollama

## Latest `develop` changes in `chataia_app.py` (since last commit)

- Added configurable model support via `OLLAMA_MODEL` (default: `llama3.1:8b`) and centralized constants.
- Replaced global shared chat history with per-session histories using Flask sessions, a session ID, and thread-safe in-memory storage.
- Added history bounding (`MAX_HISTORY_MESSAGES`) to prevent unbounded memory growth.
- Improved request validation in `/chataia`:
  - Rejects invalid JSON payloads.
  - Requires `prompt` to be a non-empty string.
- Added resilient Ollama call handling with a `503` error response when model calls fail.
- Added model availability utilities and startup validation (`_is_model_available`, `_startup_check`) to fail fast if the configured model is missing.
- Added a `/health` endpoint that reports app/model health and returns `503` when unhealthy.
- Added Flask secret key setup via `FLASK_SECRET_KEY` with a secure generated fallback.