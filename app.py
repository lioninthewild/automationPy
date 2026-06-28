import json
import os
from flask import Flask, render_template, request, jsonify
from pdf_to_audiobook import extract_text
import newspaper

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


def _parse_url(url: str) -> str:
    article = newspaper.Article(url)
    article.download()
    article.parse()
    return article.text


def _extract_pdf(path: str) -> str:
    text = extract_text(path)
    if not text.strip():
        raise ValueError("No text could be extracted from this PDF.")
    return text


# --- HTML routes (progressive enhancement fallback) ---

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_type = request.form.get("input_type", "file")
        error = None
        full_text = None

        if input_type == "text":
            full_text = request.form.get("content", "").strip()
            if not full_text:
                error = "No text provided."

        elif input_type == "file":
            file = request.files.get("pdf")
            if file and file.filename:
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)
                try:
                    full_text = _extract_pdf(filepath)
                except Exception as e:
                    error = str(e)

        return render_template("index.html",
            full_text=full_text, error=error)

    return render_template("index.html")


@app.route("/fetch-article", methods=["POST"])
def fetch_article():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="No URL provided.")
    try:
        text = _parse_url(url)
        return render_template("index.html", full_text=text)
    except Exception as e:
        return render_template("index.html",
            error=f"Failed to fetch article: {e}")


# --- JSON API endpoints (for AJAX) ---

@app.route("/api/text", methods=["POST"])
def api_text():
    content = request.form.get("content", "").strip()
    if not content:
        return jsonify(error="No text provided.")
    return jsonify(full_text=content)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    file = request.files.get("pdf")
    if not file or not file.filename:
        return jsonify(error="No file provided.")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    try:
        full_text = _extract_pdf(filepath)
        return jsonify(full_text=full_text)
    except Exception as e:
        return jsonify(error=str(e))


@app.route("/api/fetch-article", methods=["POST"])
def api_fetch_article():
    url = request.form.get("url", "").strip()
    if not url:
        return jsonify(error="No URL provided.")
    try:
        text = _parse_url(url)
        return jsonify(full_text=text)
    except Exception as e:
        return jsonify(error=f"Failed to fetch article: {e}")


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    app.run(debug=True)
