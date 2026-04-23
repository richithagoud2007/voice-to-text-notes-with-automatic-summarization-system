from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import speech_recognition as sr
from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

from flask import Flask
import nltk
import os

# ✅ Force NLTK to use a persistent folder
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")

if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

nltk.data.path.append(nltk_data_path)

# ✅ Download required tokenizer files
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading punkt...")
    nltk.download('punkt', download_dir=nltk_data_path)

# ✅ IMPORTANT: Download stopwords (required for Sumy)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading stopwords...")
    nltk.download('stopwords', download_dir=nltk_data_path)

# ✅ Flask setup
app = Flask(__name__)
app.secret_key = "secret123"

# ✅ Your existing data
users = {}
notes_history = {}

# 🔹 Summarization
def generate_summary(text):
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer

        # 🔴 Clean text (important)
        text = text.replace("\n", " ")

        # 🔴 If text too short
        if len(text.split()) < 20:
            return "Text too short to summarize."

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()

        # 🔥 Dynamic summary length
        sentence_count = max(1, len(text.split()) // 40)

        summary = summarizer(parser.document, sentence_count)

        result = " ".join([str(sentence) for sentence in summary])

        # 🔴 If still too long → cut manually
        if len(result.split()) > 50:
            result = " ".join(result.split()[:50]) + "..."

        return result

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "Unable to generate summary."
# 🔹 AI FUNCTION

def generate_summary(text):
    try:
        # ✅ Step 1: Handle empty / short text
        if not text or len(text.split()) < 20:
            return "Text too short to summarize."

        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()

        # ✅ Step 2: Try summarization
        summary_sentences = summarizer(parser.document, 1)
        summary = " ".join(str(sentence) for sentence in summary_sentences)

        # ✅ Step 3: If summary empty → fallback
        if not summary.strip():
            raise ValueError("Empty summary")

        # ✅ Step 4: Limit size
        return " ".join(summary.split()[:50]) + "..."

    except Exception as e:
        print("SUMMARY ERROR:", e)

        # 🔥 FINAL FALLBACK (ALWAYS WORKS)
        sentences = text.split('.')
        if len(sentences) > 1:
            return sentences[0] + "."
        else:
            return text

# 🔹 Home
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# 🔹 Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return "Invalid credentials"

    return render_template("login.html")

# 🔹 Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password
        notes_history[username] = []
        return redirect(url_for("login"))

    return render_template("register.html")

# 🔹 Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# 🔹 ✅ Summarize API (FIXED)
@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json()
        text = data.get("text", "")

        print("Received text:", text)  # ✅ DEBUG

        if not text.strip():
            return jsonify({"summary": "No text provided"})

        summary = generate_summary(text)

        print("Generated summary:", summary)  # ✅ DEBUG

        user = session.get("user")
        if user:
            notes_history.setdefault(user, []).append({
                "text": text,
                "summary": summary
            })

        return jsonify({"summary": summary})

    except Exception as e:
        print("🔥 FULL ERROR:", str(e))  # ✅ IMPORTANT
        return jsonify({"summary": "Error generating summary"})
# 🔹 AI Info API
@app.route("/ai-info", methods=["POST"])
def ai_info():
    data = request.get_json()
    text = data.get("text", "")
    return jsonify({"info": generate_ai_info(text)})

# 🔹 History
@app.route("/history")
def history():
    user = session.get("user")
    return jsonify(notes_history.get(user, []))

# 🔹 Run App
if __name__ == "__main__":
    app.run(debug=True)