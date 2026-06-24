import os
from flask import Flask, render_template, request
from pdf_to_audiobook import extract_text

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf")
        if file and file.filename.endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            preview = None
            error = None
            try:
                text = extract_text(filepath)
                if text.strip():
                    preview = text[:500]
                else:
                    error = "No text could be extracted from this PDF (it may be a scanned document)."
            except Exception as e:
                error = f"Failed to read PDF: {e}"

            return render_template("index.html", uploaded=file.filename, preview=preview, error=error)
    return render_template("index.html")


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)
