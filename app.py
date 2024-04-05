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

app.config['UPLOAD_FOLDER'] = '/Users/anushkasharma/Desktop/Audio_sentiment/uploads'

app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'flac', 'ogg', 'm4a'}

'''def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_wav(audio_path):
    target_path = os.path.splitext(audio_path)[0] + '.wav'
    subprocess.run(['ffmpeg', '-i', audio_path, target_path])
    os.remove(audio_path)  # Remove the original file after conversion
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
    except Exception as e:
        return "Failed to analyze sentiment due to an error with OpenAI."

def transcribe_audio_sync(audio_path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with open(audio_path, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/wav'}
        response = loop.run_until_complete(deepgram.transcription.prerecorded(source, {'punctuate': True}))
        loop.close()
        return response

@app.route('/')
def index():
    return render_template('upload.html')
@app.route('/upload', methods=['POST'])
def upload_file():
    # File presence check
    if 'audio' not in request.files:
        return jsonify(error="No file part"), 400
    
    file = request.files['audio']
    # File selection and allowed format check
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify(error="No selected file or file type not allowed"), 400
    
    filename = secure_filename(file.filename)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(audio_path)
    
    # Convert to WAV if necessary
    if filename.rsplit('.', 1)[1].lower() != 'wav':
        try:
            audio_path = convert_to_wav(audio_path)
        except Exception:
            return jsonify(error="Failed to convert the file to WAV format"), 500
    
    try:
        transcription_result = transcribe_audio_sync(audio_path)
    except Exception:
        return jsonify(error="Transcription failed due to an internal error"), 500
    
    if not transcription_result or not transcription_result.get('results', {}).get('channels', [])[0].get('alternatives', [])[0].get('transcript'):
        return jsonify(error="Could not transcribe the audio"), 500

    transcript = transcription_result['results']['channels'][0]['alternatives'][0]['transcript']
    sentiment_analysis = analyze_sentiment_with_openai(transcript)
    
    if sentiment_analysis == "Failed to analyze sentiment due to an error with OpenAI.":
        return jsonify(error=sentiment_analysis), 500
    
    return jsonify(
        message="File uploaded and transcribed successfully", 
        transcript=transcript, 
        sentiment_analysis=sentiment_analysis
    ), 200


if __name__ == '__main__':
    app.run(debug=True)'''
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_wav(audio_path):
    target_path = os.path.splitext(audio_path)[0] + '.wav'
    subprocess.run(['ffmpeg', '-i', audio_path, target_path])
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
