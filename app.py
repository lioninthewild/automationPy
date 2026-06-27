import os
from flask import Flask, render_template, request, send_from_directory
from pdf_to_audiobook import extract_text, convert_sync

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "output"


def _cleanup_folder(folder):
    for filename in os.listdir(folder):
        if filename == ".gitkeep":
            continue
        path = os.path.join(folder, filename)
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf")
        if file and file.filename:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            preview = None
            error = None
            try:
                text = extract_text(filepath)
                if text.strip():
                    preview = text[:500]
                else:
                    error = "No text could be extracted from this PDF."
            except Exception as e:
                error = f"Failed to read PDF: {e}"

            return render_template("index.html",
                uploaded=file.filename, preview=preview, error=error)

        convert_name = request.form.get("convert")
        if convert_name:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], convert_name)
            preview = None
            audio_file = None
            error = None
            voice = request.form.get("voice", "female")

            try:
                text = extract_text(filepath)
                if text.strip():
                    preview = text[:500]
                    audio_name = f"{os.path.splitext(convert_name)[0]}.mp3"
                    audio_path = os.path.join(app.config["OUTPUT_FOLDER"], audio_name)

                    convert_sync(text, audio_path, voice)
                    audio_file = audio_name
                else:
                    error = "No text could be extracted from this PDF."
            except Exception as e:
                error = f"Conversion failed: {e}"

            return render_template("index.html",
                uploaded=convert_name, preview=preview,
                audio_file=audio_file, error=error)

    return render_template("index.html")


@app.route("/cleanup", methods=["POST"])
def cleanup():
    _cleanup_folder(app.config["UPLOAD_FOLDER"])
    _cleanup_folder(app.config["OUTPUT_FOLDER"])
    return render_template("index.html", cleaned=True)


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    app.run(debug=True)
