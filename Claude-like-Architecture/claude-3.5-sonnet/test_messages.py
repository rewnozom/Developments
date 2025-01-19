import os
import sys
import requests
from datetime import datetime
import json
from time import sleep

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.conversation import Message, MessageRole

def test_message_class():
    """Test the Message class functionality"""
    print("\n=== Testing Message Class ===")
    try:
        # Create a new message
        msg = Message(
            role=MessageRole.USER,
            content="Test message",
            timestamp=datetime.now(),
            metadata={"test": True}
        )
        
        print("Original message:", msg)
        
        # Test dictionary conversion
        dict_msg = msg.to_dict()
        print("\nMessage as dictionary:", json.dumps(dict_msg, indent=2))
        
        # Test reconstruction from dictionary
        new_msg = Message.from_dict(dict_msg)
        print("\nReconstructed message:", new_msg)
        
        # Verify equality
        print("\nVerification:", "Original and reconstructed messages match" if msg.content == new_msg.content else "Messages don't match")
        
        return True
    except Exception as e:
        print(f"Error in message class test: {e}")
        return False

def test_api_endpoints():
    """Test the FastAPI endpoints"""
    print("\n=== Testing API Endpoints ===")
    base_url = "http://localhost:8000"
    
    def test_health():
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{base_url}/health")
            print("\nHealth Check:", response.json())
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def test_chat():
        url = "http://localhost:8000/chat"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "message": "Hello, how are you?",
            "conversation_id": None,
            "options": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }

        try:
            print(f"Sending request to {url}...")
            print(f"Request data: {json.dumps(data, indent=2)}")
            
            response = requests.post(url, json=data, headers=headers)
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            response_data = response.json()
            print(f"\nResponse Data: {json.dumps(response_data, indent=2)}")
            
            return response_data
            
        except requests.ConnectionError:
            print("Error: Could not connect to server. Is it running on http://localhost:8000?")
        except requests.RequestException as e:
            print(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            print(f"Raw response: {response.text}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    def test_conversations():
        """Test the conversations endpoint"""
        try:
            response = requests.get(f"{base_url}/conversations")
            print("\nConversations List:", json.dumps(response.json(), indent=2))
            return response.status_code == 200
        except Exception as e:
            print(f"Conversations test failed: {e}")
            return False

    # Run all API tests
    results = {
        "health": test_health(),
        "chat": test_chat(),
        "conversations": test_conversations()
    }
    
    return results

def main():
    """Main test function"""
    print("Starting tests...\n")
    
    # Test Message class
    message_test_result = test_message_class()
    print("\nMessage Class Test Result:", "✓ Passed" if message_test_result else "✗ Failed")
    
    # Test if server is running
    try:
        requests.get("http://localhost:8000/health")
        server_running = True
    except requests.exceptions.ConnectionError:
        server_running = False
        print("\nWarning: Server is not running. Please start the server with 'python run_server.py'")
        return

    if server_running:
        # Test API endpoints
        api_test_results = test_api_endpoints()
        
        # Print summary
        print("\n=== Test Summary ===")
        print("Message Class Tests:", "✓ Passed" if message_test_result else "✗ Failed")
        print("\nAPI Tests:")
        for endpoint, result in api_test_results.items():
            print(f"  {endpoint}: {'✓ Passed' if result else '✗ Failed'}")

if __name__ == "__main__":
    print(f"Starting test at {datetime.now()}")
    main()  # This will run all tests properly
    print("\nTest completed.")