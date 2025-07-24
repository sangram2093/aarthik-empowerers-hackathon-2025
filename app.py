from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store_manager import VectorStoreManager
from google.cloud import texttospeech
import os
import re

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/sangr/Downloads/sangram/developments/db_hackathon_2025/keyfile.json"

vector_manager = VectorStoreManager()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2, google_api_key="YOUR_KEY_HERE")

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_manager.get_vectorstore().as_retriever()
)

def clean_text(text):
    cleaned = re.sub(r'[*_~`]+', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def get_voice_params(language_code):
    voice_map = {
        'en-US': 'en-US-Standard-C',
        'hi-IN': 'hi-IN-Standard-A',
        'mr-IN': 'mr-IN-Standard-A',
        'bn-IN': 'bn-IN-Standard-A',
        'ta-IN': 'ta-IN-Standard-A',
        'te-IN': 'te-IN-Standard-A'
    }
    return voice_map.get(language_code, '')

@app.route('/')
def index():
    return render_template('frontend.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({"error": "Question not provided"}), 400
    answer = qa_chain.run(question)
    return jsonify({"answer": answer})

@app.route('/add_document', methods=['POST'])
def add_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = f"./uploaded_files/{file.filename}"
    file.save(filepath)

    try:
        vector_manager.add_document(filepath)
        return jsonify({"status": f"Document '{file.filename}' added successfully."})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get('text')
    language = data.get('language', 'en-US')

    if not text:
        return jsonify({"error": "Text not provided"}), 400

    cleaned_text = clean_text(text)
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)

    voice_name = get_voice_params(language)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    output_path = "output.mp3"
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    return send_file(output_path, mimetype='audio/mpeg')

if __name__ == '__main__':
    os.makedirs("./uploaded_files", exist_ok=True)
    app.run(debug=True, port=8080)
