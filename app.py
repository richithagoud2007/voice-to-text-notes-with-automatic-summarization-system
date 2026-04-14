from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

app = Flask(__name__)
app.secret_key = "secret123"

users = {}
notes_history = {}

# 🔹 Summarization
def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 2)
    return " ".join([str(sentence) for sentence in summary])

# 🔹 ✅ UPDATED AI FUNCTION (SMART OUTPUT)
def generate_ai_info(text):
    if not text.strip():
        return "No text provided."

    # Split into sentences
    sentences = text.split(".")
    key_points = [s.strip() for s in sentences if len(s.strip()) > 20][:3]

    # Build structured response
    result = "📌 Key Points:\n"
    for i, point in enumerate(key_points, 1):
        result += f"{i}. {point}\n"

    result += "\n🧠 Explanation:\n"
    result += "This content explains the topic in a simplified manner by focusing on the important concepts and how they are applied."

    result += "\n\n📖 Conclusion:\n"
    result += "Overall, it helps in understanding the concept clearly and quickly revising key ideas."

    return result

# 🔹 Home
@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html")
    return redirect(url_for("login"))

# 🔹 Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
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

# 🔹 Summarize API
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"summary": "No text provided"})

    summary = summarize_text(text)

    # Save history safely
    user = session.get("user")
    if user:
        notes_history.setdefault(user, []).append({
            "text": text,
            "summary": summary
        })

    return jsonify({"summary": summary})

# 🔹 AI Info API (UNCHANGED ROUTE, BETTER OUTPUT)
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