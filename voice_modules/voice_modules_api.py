from flask import Flask, request, jsonify, send_from_directory, send_file
import pyttsx3
from gtts import gTTS
import playsound
import whisper
import tempfile
import os
import requests
from utils import bark_api_tts
import jsonpickle
from flask_cors import CORS

app = Flask(__name__)
model = whisper.load_model("base")
CORS(app)

# Text-to-Speech (TTS) endpoint
@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data['text'] if data['text'] else ''
    print(text)
    if not text:
        return jsonify({'Error': 'No text provided'}), 400

    filename = bark_api_tts(text)
    
    return jsonpickle.encode({
        'audio': send_file(f'{filename}', mimetype='audio/mpeg'),
        'audio_path': filename})

# Speech-to-Text (STT) endpoint
@app.route('/stt', methods=['POST'])
def stt(audio_file = None):
    audio_file = audio_file if audio_file else request.files.get('audio')
    if not audio_file:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    audio_file.save(audio_path)

    result = model.transcribe(audio_path)
    text = result["text"]
    return jsonify({'text': text.strip()}), 200

# RASA endpoint
@app.route('/rasa', methods=['POST'])
def rasa():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({'error': 'No audio file provided'}), 400
    
    stt_response = stt(audio_file)
    print(stt_response)
    stt_response_json = stt_response[0].json
    print(stt_response_json)
    if 'error' in stt_response:
        return jsonify({'error': stt_response_json['error']}), 400
    user_text = stt_response_json['text']
    print(f'Input to RASA : {user_text}')
    
    rasa_response = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"message": user_text})
    if rasa_response.status_code != 200:
        return jsonify({'error': 'Error communicating with RASA server'}), 500
    
    rasa_response_json = rasa_response.json()
    if not rasa_response_json:
        return jsonify({'error': 'No response from RASA server'}), 500

    rasa_text = rasa_response_json[0]['text']
    print(f'Response from RASA : {rasa_text}')

    tts_response = requests.post('http://localhost:5006/tts', json={"text": rasa_text}).json()
    print(tts_response['audio_path'])
    return send_file(f'{tts_response["audio_path"]}', mimetype='audio/mpeg')
    
if __name__ == '__main__':
    app.run(port=5006, debug=True)
