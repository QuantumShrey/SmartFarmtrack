from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import logging
from google.cloud import dialogflow
import uuid

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Get API keys and project settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
if not GOOGLE_PROJECT_ID:
    raise ValueError("GOOGLE_PROJECT_ID not found in environment variables")

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# Initialize Dialogflow client
dialogflow_client = dialogflow.SessionsClient()

GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}'

def detect_intent_text(session_id, text, language_code='en'):
    """
    Detect intent from user text using Dialogflow
    """
    try:
        session = f"projects/{GOOGLE_PROJECT_ID}/agent/sessions/{session_id}"
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        
        response = dialogflow_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        
        return {
            'intent': response.query_result.intent.display_name,
            'confidence': response.query_result.intent_detection_confidence,
            'response': response.query_result.fulfillment_text,
            'parameters': dict(response.query_result.parameters)
        }
    except Exception as e:
        logger.error(f"Error in Dialogflow detection: {str(e)}")
        return None

def get_gemini_response(prompt):
    """
    Get response from Gemini API
    """
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json={
                "contents": [{"parts":[{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
        )
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.text}")
    except Exception as e:
        logger.error(f"Error in Gemini API call: {str(e)}")
        return None

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        session_id = data.get('sessionId', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
            
        # First try Dialogflow
        dialog_response = detect_intent_text(session_id, user_message)
        
        if dialog_response and dialog_response['confidence'] > 0.7:
            # Use Dialogflow's response if confidence is high
            return jsonify({
                'response': dialog_response['response'],
                'intent': dialog_response['intent'],
                'source': 'dialogflow',
                'parameters': dialog_response['parameters']
            })
        
        # Fallback to Gemini with context
        prompt = f"""As an agricultural expert assistant, please help with this farmer's query: {user_message}
        Provide a clear, practical response focusing on actionable advice."""
        
        gemini_response = get_gemini_response(prompt)
        if gemini_response:
            return jsonify({
                'response': gemini_response,
                'source': 'gemini'
            })
        else:
            raise Exception("Failed to get response from both Dialogflow and Gemini")
                
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        logger.info("Received analysis request")
        
        # Validate required fields
        required_fields = ['cropType', 'soilType', 'issues']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Call Gemini API
        prompt = f"""As an agricultural expert, analyze this farming situation:
        Crop Type: {data['cropType']}
        Soil Type: {data['soilType']}
        Issues: {data['issues']}
        
        Provide a detailed analysis including:
        1. Potential causes
        2. Recommended solutions
        3. Preventive measures
        4. Expected timeline for improvement
        """
        
        response = get_gemini_response(prompt)
        if response:
            return jsonify({'analysis': response})
        else:
            raise Exception("Failed to get analysis from Gemini API")
            
    except Exception as e:
        logger.error(f"Error in analysis endpoint: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Log startup information
    logger.info("Starting Flask server...")
    logger.info(f"API Key configured: {'Yes' if GEMINI_API_KEY else 'No'}")
    app.run(debug=True, port=5000)
