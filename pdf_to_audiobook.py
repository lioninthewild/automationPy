import argparse
import asyncio
import os
import subprocess
import tempfile
import edge_tts
import pdfplumber

VOICES = {
    "female": "en-US-JennyNeural",
    "male": "en-US-GuyNeural",
}

RATES = {
    "slow": "-20%",
    "normal": "+0%",
    "fast": "+20%",
}


def extract_text(pdf_path: str) -> str:
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def _chunk_text(text: str, max_chars: int = 10000) -> list[str]:
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


def _concat_mp3s(paths: list[str], output_path: str):
    inputs = "|".join(paths)
    try:
        subprocess.run(
            ["ffmpeg", "-i", f"concat:{inputs}", "-acodec", "copy", "-y", output_path],
            capture_output=True, check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("ffmpeg is required to merge audio chunks. Install it with: sudo pacman -S ffmpeg")


async def convert_to_audio(text: str, output_path: str, voice: str = "female", rate: str = "normal") -> str:
    chunks = _chunk_text(text)
    temp_files = []
    voice_name = VOICES.get(voice, VOICES["female"])
    rate_val = RATES.get(rate, "+0%")

    for chunk in chunks:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        communicate = edge_tts.Communicate(chunk, voice_name, rate=rate_val)
        await communicate.save(path)
        if os.path.getsize(path) > 0:
            temp_files.append(path)
        else:
            os.remove(path)

    _concat_mp3s(temp_files, output_path)

    for path in temp_files:
        os.remove(path)
    return output_path


def convert_sync(text: str, output_path: str, voice: str = "female", rate: str = "normal") -> str:
    return asyncio.run(convert_to_audio(text, output_path, voice, rate))


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to audiobook")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Save speech to an audio file (e.g. output.mp3)")
    parser.add_argument("--voice", choices=["female", "male"], default="female",
                        help="Voice to use (default: female)")
    parser.add_argument("--rate", choices=["slow", "normal", "fast"], default="normal",
                        help="Speaking speed (default: normal)")
    args = parser.parse_args()

    print(f"Extracting text from {args.pdf}...")
    text = extract_text(args.pdf)

    if not text.strip():
        print("No text could be extracted from the PDF.")
        return

    print(f"Extracted {len(text)} characters.")
    output_path = args.output or os.path.splitext(args.pdf)[0] + ".mp3"

    print("Converting to audio (this may take a while)...")
    convert_sync(text, output_path, args.voice, args.rate)
    print(f"Done! Saved to {output_path}")


if __name__ == "__main__":
    main()
