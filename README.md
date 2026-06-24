# PDF to Audiobook

A web application that converts PDF files into audio. Upload a PDF, and listen to it as speech — no need to read.

## Features

- Upload any PDF and extract its text content
- Convert text to speech using offline TTS (eSpeak-ng + pyttsx3)
- Listen to the result directly in the browser
- Also available as a CLI tool: `python pdf_to_audiobook.py <file.pdf> -o output.mp3`

## Stack

- **Backend**: Python, Flask
- **PDF parsing**: pypdf
- **Text-to-Speech**: pyttsx3 (eSpeak-ng)

## Usage

### Web app
```bash
python app.py
```
Open http://127.0.0.1:5000

### CLI
```bash
# Playback mode
python pdf_to_audiobook.py document.pdf

# Save to file
python pdf_to_audiobook.py document.pdf -o audiobook.mp3
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask pypdf pyttsx3
sudo pacman -S espeak-ng
```
