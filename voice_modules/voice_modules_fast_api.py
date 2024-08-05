from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import requests
from utils import bark_api_tts, play_ht_tts

app = FastAPI()
model = whisper.load_model("base").to('cuda')

RASA_SERVER_ENDPOINT = 'https://marlin-upright-adversely.ngrok-free.app/webhooks/rest/webhook'
TTS_ENDPOINT = 'https://formally-closing-possum.ngrok-free.app/tts'

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Text-to-Speech (TTS) endpoint
@app.post("/tts")
async def tts(request: Request):
    print("inside tts")
    data = await request.json()
    print(f'data : {data}')
    text = data.get('text', '')
    print(text)
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    print(text)
    filename = play_ht_tts(text)

    return FileResponse(path=filename, media_type='audio/mpeg')

# Speech-to-Text (STT) endpoint
@app.post("/stt")
async def stt(audio_file: UploadFile = File(...)):
    if not audio_file:
        audio_file = requests.files.get('audio')
        # raise HTTPException(status_code=400, detail="No audio file provided")
    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    with open(audio_path, 'wb') as f:
        f.write(await audio_file.read())

    result = model.transcribe(audio_path)
    text = result["text"].strip()
    return jsonable_encoder({"text": text})

# RASA endpoint
@app.post("/rasa")
async def rasa(audio_file: UploadFile = File(...)):
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    try:
        user_text = await stt(audio_file)
        user_text = user_text.get('text')
        print(f'Input to RASA : {user_text}')
    except Exception as e:
        print(f'Error during STT: {e}')
        raise HTTPException(status_code=500, detail="Error processing audio file for STT")

    try:
        rasa_response = requests.post(RASA_SERVER_ENDPOINT, json={"message": user_text})
        rasa_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error communicating with RASA server: {e}')
        raise HTTPException(status_code=500, detail="Error communicating with RASA server")

    try:
        rasa_response_json = rasa_response.json()
        rasa_text = rasa_response_json[0]['text']
        print(f'Response from RASA : {rasa_text}')
    except (ValueError, IndexError, KeyError) as e:
        print(f'Error processing RASA response: {e}')
        raise HTTPException(status_code=500, detail="Error processing RASA response")    

    # try:
    #     tts_response = requests.post(TTS_ENDPOINT, json={"text": rasa_text})
    #     tts_response.raise_for_status()
    #     # tts_response_json = tts_response.json()
    #     # audio_path = tts_response_json['audio_path']
    #     # print(f'TTS Audio Path: {audio_path}')
    # except requests.exceptions.RequestException as e:
    #     print(f'Error communicating with TTS server: {e}')
    #     raise HTTPException(status_code=500, detail="Error communicating with TTS server")
    
    try:
        tts_response_filename = play_ht_tts(rasa_text)
    except requests.exceptions.RequestException as e:
        print(f'Error communicating with TTS server: {e}')
        raise HTTPException(status_code=500, detail="Error communicating with TTS server")
    
    return FileResponse(path=tts_response_filename, media_type='audio/mpeg')
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5006)