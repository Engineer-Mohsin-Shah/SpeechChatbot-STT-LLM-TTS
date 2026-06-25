import os
import uvicorn
import base64
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from STT_To_TTS import speech_to_text_wispher, llama_model, text_to_speech_gtts

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".webm", ".ogg", ".m4a"}


def allowed_file(filename: Optional[str]) -> bool:
    if not filename:
        return False
    suffix = os.path.splitext(filename)[1].lower()
    return suffix in ALLOWED_EXTENSIONS


async def transcribe_and_speak(file: UploadFile):
    suffix = os.path.splitext(file.filename or "")[1].lower() or ".webm"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as in_file:
        in_path = in_file.name
        while chunk := await file.read(1024 * 1024):
            in_file.write(chunk)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out_file:
        out_path = out_file.name

    try:
        # STT
        text = speech_to_text_wispher(in_path)
        if not text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")

        # LLM response
        answer = llama_model(text)
        answer_text = answer.content if hasattr(answer, "content") else str(answer)

        # TTS
        text_to_speech_gtts(answer_text, output_filename=out_path)

        # Return audio in base64 for browser playback
        with open(out_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        return text, answer_text, f"data:audio/mpeg;base64,{audio_b64}"

    finally:
        try:
            os.remove(in_path)
            os.remove(out_path)
        except OSError:
            pass


@app.get("/")
async def home(request: Request):
    return FileResponse("templates/index.html")


@app.post("/api/process")
async def process(audio_file: UploadFile = File(...)):
    if not audio_file.filename or not allowed_file(audio_file.filename):
        raise HTTPException(status_code=400, detail="Please upload a valid audio file")

    transcript, reply, audio_data = await transcribe_and_speak(audio_file)

    return JSONResponse({
        "transcript": transcript,
        "reply": reply,
        "audio_data": audio_data
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
