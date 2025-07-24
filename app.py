from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from vector_store_manager import VectorStoreManager
from google.cloud import texttospeech
import os
import re
from agent import run_agricultural_agent

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/sangr/Downloads/sangram/developments/db_hackathon_2025/keyfile.json"

vector_manager = VectorStoreManager()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2, google_api_key="AIzaSyAk1XJdNVS98jfX6KS5vvKOSunxXcRNLBw")



qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_manager.get_vectorstore().as_retriever()
)
def retrieval_tool(query):
    return qa_chain.invoke(query)

def agricultural_tool(query):
    return run_agricultural_agent(query)


tools = [
    Tool(
        name="Retrieval QA",
        func=retrieval_tool,
        description=(
            "Use this tool to answer questions that require information from uploaded documents, "
            "financial schemes, government policies, subsidies, or general knowledge base queries."
        )
    ),
    Tool(
        name="Agricultural Agent",
        func=agricultural_tool,
        description=(
            "Use this tool to answer questions related to crops, weather, soil, farming practices, "
            "agricultural advice, or anything about agriculture and climate."
        )
    ),
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "system_message": (
            "You are an assistant that decides which tool to use based on the user's question. "
            "If the question is about crops, weather, soil, or agriculture, use the Agricultural Agent. "
            "If the question is about finance, government schemes, policies, or needs information from uploaded documents, use the Retrieval QA tool."
            "If the question is for both knowledge, use the both tools as well."
        )
    }
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
    answer = agent.invoke(question)
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
