import json
import queue
import requests
import sounddevice as sd
from vosk import KaldiRecognizer, Model

# Server and speech recognition configuration
FLASK_URL = "http://127.0.0.1:5000"
MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

# Thread-safe queue for incoming audio frames
q = queue.Queue()

# Initialize Vosk offline speech recognition model
print("Loading Vosk model...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
print("Vosk model loaded.")


# Audio stream callback to push raw audio bytes to the queue
def callback(indata, frames, time, status):
    if status:
        print("Audio:", status)
    q.put(bytes(indata))


# Capture microphone input and transcribe speech to text
def listen():
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        print("\n🎤 Listening...")

        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text


# Request a new chat session from the Flask backend
def create_voice_session():
    try:
        response = requests.post(f"{FLASK_URL}/new-chat", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data["session_id"]
    except Exception as error:
        print("Session error:", error)
    return None


# Send transcribed voice message to Flask server and receive AI reply
def ask_ai(text, session_id):
    try:
        response = requests.post(
            f"{FLASK_URL}/chat",
            json={"message": text, "session_id": session_id},
            timeout=120,
        )

        if response.status_code == 200:
            data = response.json()
            return (
                data.get("reply", "No response."),
                data.get("session_id", session_id),
            )

        return "Dexa server returned an error.", session_id

    except requests.exceptions.ConnectionError:
        return (
            "I cannot connect to Dexa. Please start app.py first.",
            session_id,
        )
    except requests.exceptions.Timeout:
        return "The AI took too long to respond.", session_id
    except Exception as error:
        print("Error:", error)
        return "Something went wrong.", session_id


# Main execution loop for voice interaction
def main():
    print()
    print("==============================")
    print("       DEXA ASSISTANT")
    print("==============================")
    print()
    print("Voice assistant started.")
    print("Say 'stop' to exit.")
    print()

    session_id = create_voice_session()

    if session_id:
        print("Voice chat session:", session_id)
    else:
        print("Could not create chat session.")
        return

    while True:
        command = listen()

        if not command:
            continue

        print("You:", command)

        if command.lower() in ["stop", "exit", "quit", "goodbye"]:
            print("Dexa: Goodbye!")
            break

        print("Dexa is thinking...")
        reply, session_id = ask_ai(command, session_id)

        print()
        print("Dexa:", reply)
        print()


# Application entry point
if __name__ == "__main__":
    main()