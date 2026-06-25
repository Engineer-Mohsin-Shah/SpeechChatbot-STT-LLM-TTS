import os
import pyaudio
import wave
from gtts import gTTS
from groq import Groq
import speech_recognition as sr
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv(override=True)

GROQCLOUD_API_KEY = os.getenv("GROQCLOUD_API_KEY")
client = Groq(api_key=GROQCLOUD_API_KEY)

# Specify the path to the audio file
filename = os.path.dirname(__file__) + "/English.wav"

# Audio settings
RECORD_SECONDS = 30
OUTPUT_FILE = "user_audio.wav"

# Record Audio from User and save it locally
def record_audio(output_filename, duration=RECORD_SECONDS):
    """Record audio from the microphone."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    print("Recording... Speak into the microphone.")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Recording saved to {output_filename}")


# Speech_Recognition, take speech from user. using Google Speech API
def audio_to_text_GoogleSpeechRecog():
    """Capture voice input from the user."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak into the microphone.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None


# LLM Llama Model, Ask Question
def llama_model(text):
    llm = ChatGroq(
        model='llama-3.1-8b-instant',
        api_key=GROQCLOUD_API_KEY,
        temperature=0.7)
    
    answer = llm.invoke(text)
    return answer


# Convert Speech To Text (STT) using Wispher Model
def speech_to_text_wispher(AudioFile):
    with open(AudioFile, "rb") as file:
        # Create a translation of the audio file
        translation = client.audio.translations.create(
        file=(AudioFile, file.read()), 
        model="whisper-large-v3", 
        prompt="Specify context or spelling",  
        response_format="json",  
        temperature=0.0 
        )
        text = translation.text
        return text


# gTTS Model, Text To Speech (TTS)
def text_to_speech_gtts(text, output_filename="output.mp3"):
    """Convert text to speech using gTTS."""
    tts = gTTS(text, lang="en")  # Use 'en' for English
    tts.save(output_filename)
    print(f"Audio saved as {output_filename}")
    os.system(f"start {output_filename}")  


# if __name__ == "__main__":
#     # Pass Audio directly to Wispher model
#     #text = speech_to_text_wispher(filename)

#     # Record audio and transcribe it using function
#     #record_audio(OUTPUT_FILE)
#     #print("Transcribing audio...")

#     # Record audio and convert it directly to text using google speech recognition
#     text = audio_to_text_GoogleSpeechRecog()

#     # Convert Speech to Text Using Wispher
#     #text = speech_to_text_wispher(OUTPUT_FILE)
#     #print(f"Transcribed Text: {text}")

#     print(text)
#     # Ask Question from Llama
#     answer = llama_model(text)
#     # Ensure the answer is a string
#     answer_text = answer.content
#     print(answer_text)
#     # convert Text to Speech
#     text_to_speech_gtts(answer_text)