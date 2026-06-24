import pyttsx3
import argparse
from pypdf import PdfReader


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to audiobook")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Save speech to an audio file (e.g. output.mp3)")
    args = parser.parse_args()

    print(f"Extracting text from {args.pdf}...")
    text = extract_text(args.pdf)

    if not text.strip():
        print("No text could be extracted from the PDF.")
        return

    print("Initializing TTS engine...")
    engine = pyttsx3.init()

    if args.output:
        print(f"Saving to {args.output}...")
        engine.save_to_file(text, args.output)
    else:
        print("Playing audiobook... (Press Ctrl+C to stop)")
        engine.say(text)

    engine.runAndWait()
    print("Done!")


if __name__ == "__main__":
    main()
