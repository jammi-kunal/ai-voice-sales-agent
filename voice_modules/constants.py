from pyht import Format, TTSOptions
BARK_TTS = {
    "voice_id": "IKne3meq5aSn9XLyUdCD",
    "model_id": "eleven_multilingual_v1",
    "voice_settings": {
        "stability": 0.6,
        "similarity_boost": 1,
    },
    "api_key": "sk_6e6474941a1f7ed6f138fb0ced14f2738614722695c8e7e1"
}

PLAY_TTS = {
    "user_id": "nKtTb0N524Y17GF5cTgbnmK6CuB3",
    "api_key": "db4779985f264b92b13a880957a6bdb7",
    "tts_options": TTSOptions(
        voice="s3://voice-cloning-zero-shot/a59cb96d-bba8-4e24-81f2-e60b888a0275/charlottenarrativesaad/manifest.json",
        sample_rate=44_100,
        format=Format.FORMAT_MP3,
        speed=1
    ),
    "voice_engine": "PlayHT2.0-turbo"
}

