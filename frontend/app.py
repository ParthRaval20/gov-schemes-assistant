from flask import Flask, render_template, request, jsonify, session
import warnings
import uuid
import os
import sys

warnings.filterwarnings("ignore")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# Adds gov-schemes-assistant/ to path so `rag/agent.py` can be imported
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, REPO_ROOT)

from rag.agent import ask_agent

app = Flask(__name__)
app.secret_key = "yojana-ai-secret-key-change-in-production"


@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Empty question"}), 400

    session_id = session.get("session_id", "default_user")

    try:
        result = ask_agent(question, session_id=session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    session["session_id"] = str(uuid.uuid4())
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)