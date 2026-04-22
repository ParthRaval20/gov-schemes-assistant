import os
import tempfile
import uuid
import asyncio
from flask import Flask, Response

# Mock app for testing cleanup logic
app = Flask(__name__)

async def mock_generate_speech(text, lang, path):
    with open(path, "w") as f:
        f.write(f"Speech for: {text} in {lang}")

@app.route("/test_tts")
def test_tts():
    temp_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4()}.txt")
    # Simulate speech generation
    with open(temp_path, "w") as f:
        f.write("test speech content")
    
    def generate_and_cleanup():
        print(f"DEBUG: Opening {temp_path}")
        with open(temp_path, "rb") as f:
            yield from f
        print(f"DEBUG: Closing and removing {temp_path}")
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print("DEBUG: Removed successfully")
        except Exception as e:
            print(f"DEBUG: Error removal: {e}")

    return Response(generate_and_cleanup(), mimetype="text/plain")

if __name__ == "__main__":
    print("Run this manually or use a test client to verify cleanup.")
    client = app.test_client()
    response = client.get("/test_tts")
    print(f"Response: {response.data}")
    # The file should be gone now because the generator was consumed
