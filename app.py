from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import openai
from deepgram import Deepgram
import subprocess
import asyncio
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

current_work_directory = os.getcwd()


uploads_path = os.path.join(current_work_directory, 'uploads')
app.config['UPLOAD_FOLDER'] = uploads_path


app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'flac', 'ogg', 'm4a'}
# Setup API clients
deepgram = Deepgram(deepgram_api_key)
openai.api_key = openai_api_key
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_wav(audio_path):
    target_path = os.path.splitext(audio_path)[0] + '.wav'
    subprocess.run(['ffmpeg', '-y', '-i', audio_path, target_path])
    os.remove(audio_path)  
    return target_path

def analyze_sentiment_with_openai(transcript):
    prompt = (
        "Given the following conversation, provide a detailed sentiment analysis "
        "and psychological insights. Focus on the emotional tone, any implied sentiments, "
        "and the relationship dynamics between the speakers:\n\n"
        f"{transcript}\n\n"
        "Provide your analysis with attention to subtleties and nuanced understanding of the conversation."
    )
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=0.5,
            max_tokens=300,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].text.strip()
    except Exception:
        return "Failed to analyze sentiment due to an error with OpenAI."

def transcribe_audio_sync(audio_path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with open(audio_path, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/wav'}
        response = loop.run_until_complete(deepgram.transcription.prerecorded(source, {'punctuate': True}))
        loop.close()
        return response

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    sentiment_analysis = None
    transcript = None

    if request.method == 'POST':
        if 'audio' not in request.files:
            return render_template('upload.html', error="No file part")
        
        file = request.files['audio']
        if file.filename == '' or not allowed_file(file.filename):
            return render_template('upload.html', error="No selected file or file type not allowed")
        
        filename = secure_filename(file.filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        # Overwrite the existing file if it already exists
        file.save(audio_path)
        
        if filename.rsplit('.', 1)[1].lower() != 'wav':
            audio_path = convert_to_wav(audio_path)
        
        transcription_result = transcribe_audio_sync(audio_path)
        
        if transcription_result and transcription_result.get('results', {}).get('channels', [])[0].get('alternatives', [])[0].get('transcript'):
            transcript = transcription_result['results']['channels'][0]['alternatives'][0]['transcript']
            sentiment_analysis = analyze_sentiment_with_openai(transcript)
        else:
            return render_template('upload.html', error="Could not transcribe the audio")

    return render_template('upload.html', sentiment_analysis=sentiment_analysis, transcript=transcript)

# Route to display the upload form
@app.route('/')
def index():
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

