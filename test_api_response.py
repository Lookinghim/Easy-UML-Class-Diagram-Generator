import requests
import json

# Test the API response to see what format it returns
def test_api_response():
    url = 'http://localhost:5000/api/generate-diagram'
    
    # Simple test data
    test_data = {
        "classes": [
            {
                "id": "class_1",
                "name": "TestClass",
                "attributes": [
                    {"name": "attr1", "type": "String", "visibility": "private"}
                ],
                "operations": [
                    {"name": "method1", "returnType": "void", "visibility": "public", "parameters": []}
                ],
                "connections": []
            }
        ],
        "styling": {
            "outline_width": 2,
            "outline_color": "blue"
        }
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            
            if 'image_data' in result:
                image_data = result['image_data']
                print(f"Image data type: {type(image_data)}")
                print(f"Image data starts with: {image_data[:50]}...")
                print(f"Image data length: {len(image_data)}")
                
                # Test if it's a valid data URL
                if image_data.startswith('data:image/png;base64,'):
                    print("✅ Data URL format detected")
                    base64_part = image_data.split(',')[1]
                    print(f"Base64 part length: {len(base64_part)}")
                else:
                    print("❌ Not in data URL format")
                    
            elif 'download_url' in result:
                print(f"Download URL: {result['download_url']}")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_api_response()