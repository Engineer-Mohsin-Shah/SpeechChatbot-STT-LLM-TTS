# SpeechChatbot (FastAPI STT + LLM + TTS Pipeline)

## Project Summary

SpeechChatbot is a lightweight voice chatbot built with:

- FastAPI backend
- Whisper-based speech-to-text (`Groq` audio translation endpoint)
- LLM response generation (`llama-3.1-8b-instant` via `langchain_groq`)
- Google Text-to-Speech (`gTTS`)

Users can:

- upload an audio file, or
- record directly from the browser microphone

and receive a transcript, assistant reply, and generated speech playback.

## Features

- Audio upload support for `.wav`, `.mp3`, `.webm`, `.ogg`, `.m4a`
- Browser microphone recording
- Async FastAPI route `/api/process` for processing one audio input
- Returns:
  - `transcript`
  - `reply`
  - Base64 audio payload (`audio_data`) for playback

## Quick Start

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Set required environment variable:

```bash
GROQCLOUD_API_KEY=your_groq_api_key
```

3. Run the API:

```bash
uvicorn main:app --reload
```

4. Open the UI:

```text
http://127.0.0.1:8000/
```

## API Overview

| Endpoint | Method | Input | Output | Description |
|---|---|---|---|---|
| `/` | `GET` | - | HTML page | Serves `templates/index.html` |
| `/api/process` | `POST` | `audio_file` (`UploadFile`) | JSON: `transcript`, `reply`, `audio_data` | Runs STT → LLM → TTS workflow |

## ERD-style Component View

This project does not persist user data in a database, so the “ERD” is represented as a component-relationship table to describe how each piece of the system works together.

| Entity / Component | Key Fields / Role | Relationship | How it Works |
|---|---|---|---|
| User | Audio stream / uploaded file | Sends input to | Frontend (`templates/index.html`) calls `/api/process` |
| API Route (`/api/process`) | `audio_file` | Orchestrates | Calls STT function, LLM function, TTS function |
| STT Service (`speech_to_text_wispher`) | Audio bytes, text output | Feeds | Produces `transcript` used by LLM |
| LLM Service (`llama_model`) | Transcript text | Feeds | Produces `answer_text` (assistant response) |
| TTS Service (`text_to_speech_gtts`) | `answer_text` | Produces | Generates `output.mp3` bytes (Base64 in response) |
| Response | `transcript`, `reply`, `audio_data` | Returns to | Browser shows transcript/reply and plays audio |

### ERD/Workflow Diagram (Mermaid)

```mermaid
erDiagram
    USER ||--o{ AUDIO_REQUEST : submits
    AUDIO_REQUEST ||--|| API_ROUTE : calls
    API_ROUTE ||--|| STT_RESULT : invokes
    STT_RESULT ||--|| LLM_RESPONSE : sends
    LLM_RESPONSE ||--|| TTS_OUTPUT : sends_to
    TTS_OUTPUT ||--|| CLIENT_RESPONSE : returns

    USER {
      string input_source "audio file or mic recording"
    }
    AUDIO_REQUEST {
      string audio_file
      string format "wav/mp3/webm/ogg/m4a"
    }
    API_ROUTE {
      string endpoint "/api/process"
      string method "POST"
      string status_code
    }
    STT_RESULT {
      string transcript
    }
    LLM_RESPONSE {
      string answer
    }
    TTS_OUTPUT {
      string audio_data "base64 mp3"
    }
    CLIENT_RESPONSE {
      string transcript
      string reply
      string audio_data
    }
```

## Project Files

| Path | Purpose |
|---|---|
| `main.py` | FastAPI app + routing + audio processing orchestration |
| `STT_To_TTS.py` | Core helper functions for STT, LLM, and TTS |
| `templates/index.html` | Browser UI for upload/record and playback |
| `requirements.txt` | Python dependencies |
| `data/image.png` | Testing screenshot / visual evidence |
| `data/Testing.mp4` | Testing walkthrough video |

## Testing Video & Image

![SpeechChatbot Testing Screenshot](data/image.png)

[Download/Watch Testing Video (MP4)](data/Testing.mp4)

## Notes

- The API validates incoming file extensions before processing.
- Temporary audio files are deleted after request completion.
- `STT_To_TTS.py` includes additional local/alternative helper functions for future expansion (e.g., microphone recording via `pyaudio`).

## Suggested Environment

- Python 3.12+
- Stable internet for Whisper/LLM/TTS services
- Microphone permission for browser recording
