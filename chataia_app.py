#!/usr/bin/env python
# coding: utf-8

import os
import secrets
import threading
import json

import ollama
from flask import Flask, request, render_template, jsonify, session, Response, stream_with_context

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
MAX_HISTORY_MESSAGES = 20
session_histories = {}
session_lock = threading.Lock()

def get_bot_response(messages, model=MODEL_NAME):
    response = ollama.chat(
        model=model,
        messages=messages,
    )
    return response.message.content


def stream_bot_response(messages, model=MODEL_NAME):
    return ollama.chat(
        model=model,
        messages=messages,
        stream=True,
    )


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))


def _is_model_available(model_name):
    response = ollama.list()
    if isinstance(response, dict):
        models = response.get("models", [])
    else:
        models = getattr(response, "models", [])
    names = set()
    for item in models:
        if isinstance(item, dict):
            model_id = item.get("model") or item.get("name")
        else:
            model_id = getattr(item, "model", None) or getattr(item, "name", None)
        if model_id:
            names.add(model_id)
    return model_name in names


def _startup_check():
    if not _is_model_available(MODEL_NAME):
        raise RuntimeError(
            f"Ollama model '{MODEL_NAME}' is not available. Pull it first with: "
            f"ollama pull {MODEL_NAME}"
        )


def _get_session_id():
    session_id = session.get("chat_session_id")
    if not session_id:
        session_id = secrets.token_hex(16)
        session["chat_session_id"] = session_id
    return session_id


def _get_history(session_id):
    with session_lock:
        return list(session_histories.get(session_id, []))


def _save_history(session_id, history):
    # Keep only the latest messages to avoid unbounded growth.
    bounded_history = history[-MAX_HISTORY_MESSAGES:]
    with session_lock:
        session_histories[session_id] = bounded_history


def _reset_history(session_id):
    with session_lock:
        session_histories.pop(session_id, None)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/chataia", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload."}), 400

    user_prompt = data.get("prompt", "")
    if not isinstance(user_prompt, str) or not user_prompt.strip():
        return jsonify({"error": "Field 'prompt' must be a non-empty string."}), 400

    session_id = _get_session_id()
    history = _get_history(session_id)
    user_message = {'role': 'user', 'content': user_prompt.strip()}
    messages = [*history, user_message]

    @stream_with_context
    def event_stream():
        chunks = []
        try:
            for response_chunk in stream_bot_response(messages):
                if isinstance(response_chunk, dict):
                    message_payload = response_chunk.get("message", {})
                    token = message_payload.get("content", "")
                else:
                    message_payload = getattr(response_chunk, "message", None)
                    token = getattr(message_payload, "content", "") if message_payload else ""

                if token:
                    chunks.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': f'Failed to get response from model: {exc}'})}\n\n"
            return

        full_response = "".join(chunks)
        updated_history = [*history, user_message, {"role": "assistant", "content": full_response}]
        _save_history(session_id, updated_history)
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/new-chat", methods=["POST"])
def new_chat():
    session_id = _get_session_id()
    _reset_history(session_id)
    return jsonify({"status": "ok", "message": "Chat history cleared."}), 200


@app.route("/health", methods=["GET"])
def health():
    try:
        model_available = _is_model_available(MODEL_NAME)
    except Exception as exc:
        return jsonify({"status": "unhealthy", "model": MODEL_NAME, "error": str(exc)}), 503

    if not model_available:
        return jsonify({"status": "unhealthy", "model": MODEL_NAME}), 503
    return jsonify({"status": "ok", "model": MODEL_NAME}), 200


if __name__ == '__main__':
    _startup_check()
    app.run()


