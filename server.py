import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

GEMINI_API_KEY = os.getenv('gemini_api_key')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
        
    # Prompt engineering for healthcare responses
    system_prompt = """
    You are a helpful healthcare assistant providing information about medical conditions, symptoms, treatments, and general health advice. 
    
    Guidelines:
    1. Always include appropriate medical disclaimers when necessary
    2. Provide evidence-based information when possible
    3. For serious symptoms, recommend consulting a healthcare professional
    4. Format your responses in a clear, concise manner
    5. Use empathetic language
    6. Break complex information into digestible parts
    7. If you're unsure about something, acknowledge your limitations
    8. Focus on providing general health information, not personalized medical advice
    9. For emergency situations, emphasize the importance of seeking immediate medical attention
    
    Remember that you are not a replacement for professional medical care.
    """
    
    try:
        # Create a chat session with the system prompt and user message
        response = model.generate_content(
            [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I understand. I'll act as a helpful healthcare assistant within these guidelines."]},
                {"role": "user", "parts": [user_message]}
            ]
        )
        print(response.text)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f"Sorry, there was an error contacting the AI service: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
