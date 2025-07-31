"""
AI PDF Reader Web Application
================================

This Flask application provides a very simple PDF reader and chat interface
that talks to the DeepSeek API.  Users can upload a PDF, the server will
extract the text from the document, and the user can then ask questions
about the document.  Questions are forwarded to the DeepSeek chat
completion endpoint together with the extracted PDF text to produce
context‑aware answers.

To use this application you need to supply a valid DeepSeek API key via
the ``DEEPSEEK_API_KEY`` environment variable.  You can obtain an API
key by signing up at the DeepSeek platform.  The DeepSeek API is
compatible with the OpenAI format, so the payload you send to
``https://api.deepseek.com/chat/completions`` closely resembles the
OpenAI Chat Completions API【125360099820378†screenshot】【80667180641075†screenshot】.

Running locally
---------------

Install the dependencies and start the Flask development server:

.. code-block:: bash

   pip install -r requirements.txt
   export DEEPSEEK_API_KEY=sk‑...           # your DeepSeek API key
   python app.py

Then open ``http://localhost:5000`` in your browser to use the app.

This application is intentionally simple and stores the uploaded PDF
text and conversation history in memory.  Do not use it in production
without adding proper session management, input validation and error
handling.  The goal is to demonstrate how to call the DeepSeek API from
Python and build a chat UI around PDF documents.
"""

import os
from typing import List, Dict, Any

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from PyPDF2 import PdfReader


app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Global variables to keep the extracted PDF text and conversation history.
# In a real world application you would want to persist this state per
# session or user.  Here we keep it simple and store it in memory.
PDF_TEXT: str = ""
conversation_history: List[Dict[str, str]] = []

# The DeepSeek API key is read from the environment.  If it is not set
# the server will return an error when attempting to call the API.
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


@app.route("/")
def index() -> Any:
    """Serve the single page application."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/upload", methods=["POST"])
def upload_pdf() -> Any:
    """Handle PDF uploads and extract text from the document.

    The endpoint expects a multipart/form-data request with a ``file``
    parameter containing the PDF.  It uses PyPDF2 to read the PDF and
    concatenates the extracted text from all pages.  The extracted text
    is stored in the global ``PDF_TEXT`` variable and a preview of the
    first few thousand characters is returned to the client.
    """
    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({"error": "No PDF file uploaded."}), 400

    try:
        reader = PdfReader(uploaded_file)
        text_parts: List[str] = []
        for page in reader.pages:
            # extract_text can return None for some pages; default to empty
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        extracted = "\n".join(text_parts)
    except Exception as exc:
        return jsonify({"error": f"Failed to parse PDF: {exc}"}), 500

    # Store globally and reset conversation history
    global PDF_TEXT, conversation_history
    PDF_TEXT = extracted
    conversation_history = []

    # Return a preview to the client so they know the PDF was processed.
    preview = extracted[:2000]  # first 2000 characters
    return jsonify({"message": "PDF uploaded successfully.", "preview": preview})


@app.route("/ask", methods=["POST"])
def ask_question() -> Any:
    """Handle user questions and forward them to the DeepSeek API.

    The JSON body must contain a ``question`` field.  If no PDF has been
    uploaded yet the request will fail.  The function constructs a
    message list consisting of a system prompt, the (truncated) PDF text,
    the conversation history and the new question.  This list is sent
    as part of the payload to the DeepSeek chat completion endpoint.
    """
    if not PDF_TEXT:
        return jsonify({"error": "No PDF uploaded yet."}), 400

    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "DeepSeek API key not configured on server."}), 500

    # Build the messages for the chat API.  The system prompt tells the
    # model what to do.  We include the PDF text as an additional system
    # message to give the model context.  To avoid hitting the model's
    # context limit we truncate the text.  Adjust ``max_context_chars``
    # depending on the size of your PDFs and model context window.
    max_context_chars = 8000
    truncated_pdf = PDF_TEXT[:max_context_chars]

    messages: List[Dict[str, str]] = []
    messages.append({
        "role": "system",
        "content": (
            "You are an assistant that answers questions about a PDF. "
            "Answer the user's question using only the information in the provided PDF. "
            "If the answer cannot be found in the PDF, say you don't know."
        )
    })
    messages.append({"role": "system", "content": truncated_pdf})
    # Append previous conversation so the model has context of what has
    # already been asked and answered.
    for msg in conversation_history:
        messages.append(msg)
    # Append the latest question
    messages.append({"role": "user", "content": question})

    payload: Dict[str, Any] = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            json=payload,
            headers=headers,
            timeout=60,
        )
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": f"Failed to call DeepSeek API: {exc}"}), 500

    if resp.status_code != 200:
        return jsonify({"error": "DeepSeek API returned an error.", "details": resp.text}), 500

    try:
        result = resp.json()
        answer = result["choices"][0]["message"]["content"]
    except Exception as exc:
        return jsonify({"error": f"Invalid response from DeepSeek API: {exc}"}), 500

    # Update conversation history: include both user question and assistant answer.
    conversation_history.append({"role": "user", "content": question})
    conversation_history.append({"role": "assistant", "content": answer})

    return jsonify({"answer": answer})


@app.errorhandler(404)
def page_not_found(_: Any) -> Any:
    """Return the index for any unknown route so that front‑end routing works."""
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":  # pragma: no cover
    # Use environment variable PORT if set, otherwise default to 5000.
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
