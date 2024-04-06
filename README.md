# Audio Sentiment Analysis Web Application

## Project Overview
This web application allows hiring managers to upload audio files of dialogues and receive sentiment and psychological insights about the conversation. The application uses the Deepgram API for speech-to-text transcription and the OpenAI API for sentiment analysis.

## Technologies Used
- Flask (A Python web framework)
- Deepgram API (For speech-to-text transcription)
- OpenAI API (For sentiment analysis)
- Python libraries: `os`, `subprocess`, `openai`, `asyncio`

## Setup and Installation
1. Ensure Python is installed on your system.
2. Clone the repository to your local machine.
3. Install the required dependencies:
```pip install -r requirements.txt```

4. Set up environment variables for `DEEPGRAM_API_KEY` and `OPENAI_API_KEY`.

## Running the Application Locally
1. Navigate to the project directory in your terminal.
2. Run the Flask application:

```flask run```

3. Open your web browser and go to `http://127.0.0.1:5000/` to access the web interface.

## Using the Application
1. Click on the "Upload" button and select an audio file with a conversation.
2. The application will process the file and display sentiment and psychological insights derived from the conversation.

## Deployment
This application is deployed on a Virtual Machine on Google Cloud Platform : ``` http://34.130.102.62 ```


## Challenges Faced
- Handling asynchronous API calls within the synchronous Flask framework.
- Refining the OpenAI prompt for more nuanced sentiment analysis.
- Ensuring reliable conversion of various audio formats to `.wav`.

## Future Enhancements
- Improve the UI/UX of the web interface.
- Implement more advanced error handling and logging for production use.
- Explore the use of WebSocket for real-time updates to the user while processing files.




