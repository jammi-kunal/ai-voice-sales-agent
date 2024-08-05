import requests
import tempfile
from pyht import Client
from constants import BARK_TTS, PLAY_TTS

def bark_api_tts(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{BARK_TTS['voice_id']}"
    payload = {
        "text": text,
        "model_id": BARK_TTS['model_id'],
        "voice_settings": BARK_TTS['voice_settings'],
    }
    headers = {
        "xi-api-key": BARK_TTS["api_key"],
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix='.mp3') as fp:
        filename = fp.name
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                fp.write(chunk)
    print(filename)
    return filename

def play_ht_tts(text):
    client = Client(PLAY_TTS["user_id"], PLAY_TTS["api_key"])
    response = client.tts(text=text, voice_engine="PlayHT2.0-turbo", options=PLAY_TTS["tts_options"])
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix='.mp3') as fp:
        filename = fp.name
        for chunk in response:
            if chunk:
                fp.write(chunk)
    print(f"Response filepath : {filename}")
    return filename