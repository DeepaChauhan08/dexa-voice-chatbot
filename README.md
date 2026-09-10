# dexa-voice-chatbot
A clean, responsive To-Do List web a# Dexa - Voice & Text AI Chatbot

Dexa is a multimodal personal AI assistant combining a Flask REST backend with offline speech recognition and local LLM inference. It supports multi-session conversations, automatic title generation, SQLite message persistence, and hands-free voice commands.

## Features

- **Local LLM Inference**: Powered by local models running via Ollama (`tinyllama:latest` by default).
- **Offline Voice Recognition**: Transcribes microphone input in real time using the lightweight Vosk Kaldi speech engine (`vosk-model-small-en-us-0.15`).
- **Session Management**: Automatically organizes conversations into sessions with auto-generated titles based on prompt context.
- **Persistent Conversation History**: Stores user profiles, sessions, and timestamps locally via an SQLite database with cascade deletes.
- **RESTful API**: Clean Flask endpoints for session creation, history lookup, messaging, and chat clearing.

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **LLM Runtime**: Ollama
- **Speech-to-Text**: Vosk, SoundDevice
- **Database**: SQLite3
- **Audio Processing**: NumPy / Raw PCM (16 kHz, 16-bit mono)

## Project Structure

```text
├── app.py                      # Flask REST API server and Ollama integration
├── assistant.py                # Voice client for microphone capture and STT
├── database.py                 # SQLite database schema, connections, and CRUD
├── dexa.db                     # SQLite database file (auto-generated)
├── templates/
│   └── index.html              # Web UI chat interface
├── vosk-model-small-en-us-0.15/ # Offline speech recognition model folder
└── README.mdpplication built with vanilla HTML5, CSS3, and JavaScript featuring task addition, completion marking, and removal.
