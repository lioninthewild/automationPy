import argparse
import os
import struct
import tempfile
import re
import wave
import pyttsx3
import pdfplumber


def extract_text(pdf_path: str) -> str:
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def _chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(" ".join(current)) >= max_chars:
            chunks.append(" ".join(current[:-1]))
            current = [word]

    if current:
        chunks.append(" ".join(current))

    return [c for c in chunks if c.strip()]


def _concat_wavs(paths: list[str], output_path: str):
    data_chunks = []
    params = None
    for path in paths:
        with wave.open(path, "rb") as w:
            if params is None:
                params = w.getparams()
            data_chunks.append(w.readframes(w.getnframes()))

    with wave.open(output_path, "wb") as out:
        out.setparams(params)
        out.writeframes(b"".join(data_chunks))


def convert_to_audio(text: str, output_path: str) -> str:
    chunks = _chunk_text(text)
    temp_files = []

    engine = pyttsx3.init()

    for i, chunk in enumerate(chunks):
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        engine.save_to_file(chunk, path)
        engine.runAndWait()
        if os.path.getsize(path) > 44:
            temp_files.append(path)
        else:
            os.remove(path)

    _concat_wavs(temp_files, output_path)

    for path in temp_files:
        os.remove(path)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to audiobook")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Save speech to an audio file (e.g. output.wav)")
    args = parser.parse_args()

    print(f"Extracting text from {args.pdf}...")
    text = extract_text(args.pdf)

    if not text.strip():
        print("No text could be extracted from the PDF.")
        return

    print(f"Extracted {len(text)} characters.")
    output_path = args.output or os.path.splitext(args.pdf)[0] + ".wav"

    print("Converting to audio (this may take a while)...")
    convert_to_audio(text, output_path)
    print(f"Done! Saved to {output_path}")


if __name__ == "__main__":
    main()
