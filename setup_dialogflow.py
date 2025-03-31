from google.cloud import dialogflow
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Debug print current directory
print(f"Current directory: {os.getcwd()}")

# Load environment variables with explicit path
env_path = Path('.env')
print(f"Looking for .env file at: {env_path.absolute()}")
if env_path.exists():
    print(".env file found")
    load_dotenv(env_path)
else:
    print(".env file not found!")

# Debug print loaded environment variables
print("\nLoaded Environment Variables:")
print(f"GOOGLE_PROJECT_ID: {os.getenv('GOOGLE_PROJECT_ID')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

def verify_setup():
    """Verify all required credentials and files exist"""
    required_vars = {
        'GOOGLE_PROJECT_ID': os.getenv('GOOGLE_PROJECT_ID'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    }
    
    # Check environment variables
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
        
    # Check if credentials file exists
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not os.path.exists(creds_path):
        print(f"Credentials file not found at: {creds_path}")
        return False
        
    # Verify JSON file is valid
    try:
        with open(creds_path, 'r') as f:
            json.load(f)
        print("Credentials file is valid JSON")
    except json.JSONDecodeError:
        print("Credentials file is not valid JSON")
        return False
    except Exception as e:
        print(f"Error reading credentials file: {str(e)}")
        return False
        
    print("All setup requirements verified!")
    return True

def create_dialogflow_agent():
    """Create a new Dialogflow agent programmatically"""
    try:
        client = dialogflow.AgentsClient()
        project_id = os.getenv('GOOGLE_PROJECT_ID')
        parent = f"projects/{project_id}"
        
        agent = {
            "parent": parent,
            "display_name": "FarmtrackAssistant",
            "default_language_code": "en",
            "time_zone": "Asia/Kolkata",
            "enable_logging": True,
            "match_mode": "MATCH_MODE_HYBRID",
            "api_version": "API_VERSION_V2"
        }
        
        # Use set_agent instead of create_agent
        response = client.set_agent(agent=agent)
        print(f"Agent created/updated successfully in project: {project_id}")
        return response
    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        return None

def create_basic_intents():
    """Create basic intents for farming queries"""
    try:
        client = dialogflow.IntentsClient()
        parent = f"projects/{os.getenv('GOOGLE_PROJECT_ID')}/agent"
        
        # Define basic intents
        intents = [
            {
                "display_name": "crop_disease",
                "training_phrases": [
                    "my tomatoes have spots on leaves",
                    "plants showing yellow patches",
                    "what's wrong with my crops",
                    "disease in my farm",
                    "pest problem in crops"
                ],
                "message_texts": [
                    "Based on your description, this might be {disease}. I recommend: \n1. Inspect the affected areas\n2. Check for spreading patterns\n3. Consider soil testing\n\nWould you like specific treatment recommendations?"
                ]
            },
            {
                "display_name": "soil_query",
                "training_phrases": [
                    "is my soil good for wheat",
                    "best soil type for rice",
                    "soil requirements for farming",
                    "soil fertility check",
                    "what can I grow in clay soil"
                ],
                "message_texts": [
                    "For optimal farming, your soil type is suitable for {crops}. Consider:\n1. pH levels\n2. Organic matter content\n3. Drainage characteristics\n\nWould you like specific crop recommendations?"
                ]
            },
            {
                "display_name": "weather_impact",
                "training_phrases": [
                    "will rain affect my crops",
                    "temperature impact on harvest",
                    "protect crops from frost",
                    "weather forecast for farming",
                    "drought effects on plants"
                ],
                "message_texts": [
                    "Based on the weather conditions:\n1. Expected impact: {impact}\n2. Recommended actions: {actions}\n3. Preventive measures: {measures}\n\nWould you like specific protection strategies?"
                ]
            }
        ]
        
        for intent_data in intents:
            training_phrases = []
            for phrase in intent_data["training_phrases"]:
                part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
                training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
                training_phrases.append(training_phrase)

            message_text = dialogflow.Intent.Message.Text(
                text=intent_data["message_texts"]
            )
            message = dialogflow.Intent.Message(text=message_text)

            intent = dialogflow.Intent(
                display_name=intent_data["display_name"],
                training_phrases=training_phrases,
                messages=[message]
            )

            response = client.create_intent(
                request={"parent": parent, "intent": intent}
            )
            print(f"Intent created: {response.display_name}")
            
    except Exception as e:
        print(f"Error creating intents: {str(e)}")

if __name__ == "__main__":
    print("Verifying setup...")
    if verify_setup():
        print("Creating Dialogflow agent...")
        agent = create_dialogflow_agent()
        if agent:
            print("Creating basic intents...")
            create_basic_intents()
            print("Setup completed successfully!")
        else:
            print("Failed to create agent. Please check your credentials and permissions.")
    else:
        print("Setup verification failed. Please check your credentials and permissions.")
