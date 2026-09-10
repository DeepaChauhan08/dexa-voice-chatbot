from flask import Flask, jsonify, render_template, request
import requests

from database import (
    clear_all_history,
    create_session,
    delete_session,
    get_messages,
    get_recent_messages,
    get_session,
    get_sessions,
    init_db,
    save_message,
    update_session_title,
)

# Initialize Flask application
app = Flask(__name__)

# Ollama API configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "tinyllama:latest"

# Initialize database schema
init_db()


# Query the Ollama language model with session history
def ask_ai(session_id: int) -> str:
    previous_messages = get_recent_messages(session_id, 20)

    messages = [
        {
            "role": "system",
            "content": (
                "You are Dexa, a helpful personal AI assistant. "
                "Answer clearly, naturally and helpfully. "
                "Keep answers reasonably concise unless the user asks for details."
            ),
        }
    ]

    for message in previous_messages:
        messages.append({
            "role": message["role"],
            "content": message["content"],
        })

    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=120)

        if response.status_code != 200:
            print("Ollama Error:", response.text)
            return "Sorry, Ollama returned an error."

        result = response.json()
        return result["message"]["content"]

    except requests.exceptions.ConnectionError:
        return "Ollama is not running. Please start Ollama first."
    except requests.exceptions.Timeout:
        return "Ollama took too long to respond."
    except Exception as error:
        print("Ollama Error:", error)
        return "Something went wrong while connecting to the AI."


# Render home page UI
@app.route("/")
def home():
    return render_template("index.html")


# Create a new chat session
@app.route("/new-chat", methods=["POST"])
def new_chat():
    session_id = create_session()
    return jsonify({
        "success": True,
        "session_id": session_id,
    })


# Retrieve list of all chat sessions
@app.route("/sessions", methods=["GET"])
def sessions():
    sessions_data = get_sessions()
    result = [
        {
            "id": session["id"],
            "title": session["title"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
        }
        for session in sessions_data
    ]
    return jsonify(result)


# Retrieve message history for a specific chat session
@app.route("/history/<int:session_id>", methods=["GET"])
def history(session_id: int):
    session = get_session(session_id)

    if session is None:
        return jsonify({"error": "Chat not found"}), 404

    messages = get_messages(session_id)
    result = [
        {
            "id": message["id"],
            "role": message["role"],
            "content": message["content"],
            "created_at": message["created_at"],
        }
        for message in messages
    ]

    return jsonify({
        "session": {
            "id": session["id"],
            "title": session["title"],
        },
        "messages": result,
    })


# Handle sending user prompt, saving history, and receiving AI response
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data:
        return jsonify({"reply": "Invalid request."}), 400

    message = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    if not session_id:
        session_id = create_session()
    else:
        session = get_session(session_id)
        if session is None:
            session_id = create_session()

    save_message(session_id, "user", message)
    reply = ask_ai(session_id)
    save_message(session_id, "assistant", reply)

    session = get_session(session_id)
    if session and session["title"] == "New Chat":
        title = message[:35]
        if len(message) > 35:
            title += "..."
        update_session_title(session_id, title)

    return jsonify({
        "reply": reply,
        "session_id": session_id,
    })


# Delete a specific chat session by ID
@app.route("/delete-chat/<int:session_id>", methods=["DELETE"])
def delete_chat(session_id: int):
    delete_session(session_id)
    return jsonify({"success": True})


# Clear all sessions and conversation history
@app.route("/clear-history", methods=["DELETE"])
def clear_history():
    clear_all_history()
    return jsonify({"success": True})


# Run local Flask development server
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )