from flask import Flask, json, request, jsonify, send_file, render_template
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
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from typing import Union, List
from dotenv import load_dotenv
from google.oauth2 import service_account

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/sangr/Downloads/sangram/developments/db_hackathon_2025/keyfile.json"

load_dotenv()

vector_manager = VectorStoreManager()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2, google_api_key=os.getenv("API_KEY"))



qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_manager.get_vectorstore().as_retriever()
)
class RobustOutputParser(ReActSingleInputOutputParser):
    """Custom parser that handles various LLM output formats"""
    
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        """Parse LLM output with robust error handling"""
        try:
            # First try the standard ReAct parsing
            return super().parse(text)
        except Exception:
            # If standard parsing fails, check for common patterns
            text_lower = text.lower().strip()
            
            # Check if it's trying to use a tool
            if "action:" in text_lower or "tool:" in text_lower:
                try:
                    # Extract tool name and input
                    lines = text.split('\n')
                    action_line = None
                    input_line = None
                    
                    for line in lines:
                        if line.lower().startswith('action:') or line.lower().startswith('tool:'):
                            action_line = line.split(':', 1)[1].strip()
                        elif line.lower().startswith('action input:') or line.lower().startswith('input:'):
                            input_line = line.split(':', 1)[1].strip()
                    
                    if action_line and input_line:
                        return AgentAction(
                            tool=action_line,
                            tool_input=input_line,
                            log=text
                        )
                except:
                    pass
            
            # If it looks like a direct answer, treat as final
            return AgentFinish(
                return_values={"output": text.strip()},
                log=text
            )

# Tool wrapper functions with better formatting
def safe_retrieval_tool(query: str) -> str:
    """Safe wrapper for retrieval tool"""
    try:
        result = qa_chain.invoke({"query": query})
        if isinstance(result, dict):
            return result.get('result', str(result))
        return str(result)
    except Exception as e:
        return f"I couldn't retrieve specific document information, but I can provide general guidance on your query: {query}"

async def safe_agricultural_tool(query: str) -> str:
    """Safe wrapper for agricultural tool with structured output"""
    try:
        result = await run_agricultural_agent(query)
        
        # Handle different result types
        if isinstance(result, dict):
            return json.dumps(result, indent=2, ensure_ascii=False)
        elif isinstance(result, str):
            return result 
        # return result 
        else:
            return str(result)
    except Exception as e:
        return f"I couldn't retrieve specific document information, but I can provide general guidance on your query: {query}"

tools = [
    Tool(
        name="Retrieval QA",
        func=safe_retrieval_tool,
        description=(
            "Use this tool to answer questions that require information from uploaded documents, "
            "financial schemes, government policies, subsidies, or general knowledge base queries."
        )
    ),
    Tool(
        name="Agricultural Agent",
        func=safe_agricultural_tool,
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
    max_iterations=3,
    early_stopping_method="generate",
    output_parser=RobustOutputParser(),   
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": (
            "You are an assistant that decides which tool to use based on the user's question. "
            "If the question is about crops, weather, soil, or agriculture, use the Agricultural Agent. "
            "If the question is about finance, government schemes, policies, or needs information from uploaded documents, use the Retrieval QA tool."
            "If the question is for both knowledge, use the both tools as well."
            "give output in a structured format giving just the input and output"
        )
    }
)

def clean_text(text):
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
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
    print("\n\n\n\n\n\n\n") 
    print("Received question:", question)
    print("\n\n\n\n\n\n\n") 
    print("\n\n\n\n\n\n\n") 
    if not question:
        return jsonify({"error": "Question not provided"}), 400
    answer = agent.invoke(question)
    # print("\n\n\n\n\n\n\n") 
    # print(answer)
    # print(answer["output"])
    # print("\n\n\n\n\n\n\n") 
    return jsonify({"answer": answer["output"]})

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
    credentials = service_account.Credentials.from_service_account_file(r"C:\Users\91702\Desktop\workspace\hackathon\aarthik-empowerers-hackathon-2025\keyfile.json")
    client = texttospeech.TextToSpeechClient(credentials=credentials)
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
