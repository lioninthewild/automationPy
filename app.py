import os
from flask import Flask, render_template, request
from pdf_to_audiobook import extract_text
import newspaper

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_type = request.form.get("input_type", "file")
        error = None
        full_text = None

        # --- Text input ---
        if input_type == "text":
            full_text = request.form.get("content", "").strip()
            if not full_text:
                error = "No text provided."

        # --- File upload ---
        elif input_type == "file":
            file = request.files.get("pdf")
            if file and file.filename:
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)
                try:
                    full_text = extract_text(filepath)
                    if not full_text.strip():
                        error = "No text could be extracted from this PDF."
                except Exception as e:
                    error = f"Failed to read PDF: {e}"

        return render_template("index.html",
            full_text=full_text, error=error)

    return render_template("index.html")


@app.route("/fetch-article", methods=["POST"])
def fetch_article():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="No URL provided.")
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        text = article.text
        if text.strip():
            return render_template("index.html",
                full_text=text)
        else:
            return render_template("index.html",
                error="Could not extract any text from this URL.")
    except Exception as e:
        return render_template("index.html",
            error=f"Failed to fetch article: {e}")


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    app.run(debug=True)
