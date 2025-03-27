import requests
import json

try:
    response = requests.get('http://localhost:5000/api/test')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Make a test crop analysis request
    test_data = {
        "cropType": "wheat",
        "soilType": "loamy",
        "issues": "yellow leaves"
    }
    
    analysis = requests.post('http://localhost:5000/api/analyze', json=test_data)
    print("\nAnalysis Test:")
    print(f"Status Code: {analysis.status_code}")
    print(f"Response: {json.dumps(analysis.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {str(e)}")
