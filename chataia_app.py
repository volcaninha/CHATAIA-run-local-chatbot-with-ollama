#!/usr/bin/env python
# coding: utf-8

import ollama
from flask import Flask, request, render_template, jsonify
import json

chat_history = []

def get_bot_response(messages, model="llama3.1:8b"):
    response = ollama.chat(
        model=model,
        messages=messages,
    )
    return response.message.content
    

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/chataia", methods=["POST"])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    messages=[*chat_history, {'role':'user', 'content':user_prompt}]
    bot_response=get_bot_response(messages)

    # javascript in html expects json format
    return jsonify({"response": bot_response})


if __name__ == '__main__':
    app.run()


