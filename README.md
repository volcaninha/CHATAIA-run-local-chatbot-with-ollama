# :mushroom: CHATAIA-run-local-chatbot-with-ollama

## Local AI Chatbot with Flask + Ollama

A lightweight AI chatbot built with **Flask** and **Ollama** that runs locally using open-source language models like ```llama3.1:8b```.  
The application supports session-based chat history, JSON API endpoints, health checks, and a simple web interface.

## Features :bulb:

- Flask backend with REST API
- Real-time streaming responses from Ollama (token-by-token)
- Configurable AI model support via environment variable `OLLAMA_MODEL` (default: `llama3.1:8b`)
- JSON request validation
- Session-based conversation memory using Flask session IDs
- "New Chat" button in the UI to instantly clear the current session conversation
- Flask secret key setup via `FLASK_SECRET_KEY`
- History bounding (`MAX_HISTORY_MESSAGES`) to prevent unbounded memory growth
- Automatic model availability validation on startup (`_is_model_available`, `_startup_check`)
- GET /health endpoint that reports model/app readiness and returns `503` when unhealthy
- POST /new-chat endpoint to reset in-memory chat history for the current browser session

## Prerequisites :briefcase:

Before running the app, install and prepare:

- Python 3.9+ (recommended).
- `uv` for Python project and dependency management.
- [Ollama](https://ollama.com/) installed and running locally.
- An available Ollama model (default: `llama3.1:8b`).

Example to pull the default model:

```bash
ollama pull llama3.1:8b
```

## How to use

1. Clone the Repository
```bash
git clone https://github.com/volcaninha/CHATAIA-run-local-chatbot-with-ollama.git
```

2. Install/sync Python dependencies with `uv`:

```bash
uv sync
```

If this project does not yet declare dependencies, add them first:

```bash
uv add flask ollama
```

You may also want to run it in a WSGI framework, then add:

```bash
uv add gunicorn
```

3. (Optional) Configure environment variables:

```bash
export OLLAMA_MODEL="llama3.1:8b"
export FLASK_SECRET_KEY="your-strong-random-secret"
```

4. Start the Flask app:

```bash
uv run gunicorn chataia_app:app
```
 
Or, using the flask built-in server which is meant only for development/local testing:

```bash
uv run python chataia_app.py
```

5. Open the UI in your browser:

```text
http://127.0.0.1:8000/
```

6. Verify health endpoint (optional):

```bash
curl http://127.0.0.1:8000/health
```

7. Send a chat request directly (optional, streaming output):

```bash
curl -N -X POST http://127.0.0.1:8000/chataia \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, who are you?"}'
```

You will receive a stream of `data:` events (Server-Sent Events style), for example:

```text
data: {"token":"Hello"}

data: {"token":" there!"}

data: {"done":true}
```

8. Start a fresh conversation without reloading (optional):

From the web UI, click **New Chat** to clear the chat window and reset the backend history for your current session.
You can also call the endpoint directly:

```bash
curl -X POST http://127.0.0.1:8000/new-chat
```

## :loudspeaker: Error Handling

The applicatiob includes validation and error handling for:

- Invalid JSON requests
- Empty prompts
- Missing Ollama models
- Ollama server failures

## :balance_scale: License

This project is licensed under the MIT License. Feel free to use, modify, and share this code.