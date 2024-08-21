from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
from io import BytesIO

app = FastAPI()
translator = Translator()
recognizer = sr.Recognizer()

@app.post("/translate-audio/")
async def translate_audio(file: UploadFile = File(...), target_lang: str = "ta"):
    try:
        # Read the uploaded file
        audio_data = await file.read()

        # Convert to a format readable by speech_recognition
        audio = AudioSegment.from_file(BytesIO(audio_data))
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio_bytes = BytesIO()
        audio.export(audio_bytes, format="wav")
        audio_bytes.seek(0)

        # Convert audio to text
        with sr.AudioFile(audio_bytes) as source:
            audio_content = recognizer.record(source)
            text = recognizer.recognize_google(audio_content)
            print(f"Recognized Text: {text}")

        # Translate the text
        translated_text = translator.translate(text, dest=target_lang).text
        print(f"Translated Text: {translated_text}")

        # Return the translated text as a response
        return JSONResponse(content={"translated_text": translated_text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)