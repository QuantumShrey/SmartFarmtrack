from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')

# Enable CORS
CORS(app)

GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}'

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

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
        headers = {
            'Content-Type': 'application/json'
        }
        
        prompt = f"""As an agricultural expert AI, analyze the following crop data and provide detailed recommendations:

Crop Details:
- Type: {data['cropType']}
- Soil Type: {data['soilType']}
- Current Issues: {data['issues']}

Please provide specific recommendations for:
1. How to address the current issues
2. Best practices for this crop and soil combination
3. Preventive measures for common problems
4. Optimal irrigation and care guidelines

Format the response in clear, farmer-friendly language with bullet points."""
            
        gemini_payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024
            }
        }
        
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=gemini_payload
        )
        
        if response.status_code != 200:
            error_message = f"Gemini API error: Status {response.status_code}, Response: {response.text}"
            logger.error(error_message)
            return jsonify({
                'success': False,
                'error': error_message
            }), 500
            
        ai_response = response.json()
        ai_recommendation = ai_response['candidates'][0]['content']['parts'][0]['text']
        
        # Return success response
        return jsonify({
            'success': True,
            'recommendations': {
                'content': ai_recommendation
            }
        })
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test', methods=['GET', 'OPTIONS'])
def test_connection():
    """Test endpoint to verify API is working"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Test the model with a simple prompt
        test_response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            json={
                "contents": [{
                    "parts": [{
                        "text": "Say hello"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'API is working',
            'api_key_configured': bool(GEMINI_API_KEY),
            'model_name': 'gemini-1.5-flash',
            'server_status': 'running',
            'model_test': test_response.json()['candidates'][0]['content']['parts'][0]['text'] if test_response else None
        })
    except Exception as e:
        logger.error(f"API test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Log startup information
    logger.info("Starting Flask server...")
    logger.info(f"API Key configured: {'Yes' if GEMINI_API_KEY else 'No'}")
    logger.info("Using Gemini 1.5 Flash model")
    
    # Run the app on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
