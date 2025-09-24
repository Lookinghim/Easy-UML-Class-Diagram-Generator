#!/usr/bin/env python3

"""
Test script to demonstrate the complete UML web application functionality
This script tests the Flask API endpoints directly
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoints():
    """Test all API endpoints"""
    
    print("UML Web Application API Test")
    print("=" * 40)
    
    # Test data - create sample classes
    sample_classes = [
        {
            "id": "1",
            "name": "User",
            "attributes": [
                {"id": "1", "name": "username", "type": "String", "visibility": "private"},
                {"id": "2", "name": "email", "type": "String", "visibility": "private"},
                {"id": "3", "name": "id", "type": "int", "visibility": "public"}
            ],
            "operations": [
                {"id": "1", "name": "getUsername()", "visibility": "public"},
                {"id": "2", "name": "setUsername(String)", "visibility": "public"},
                {"id": "3", "name": "validateEmail()", "visibility": "private"}
            ],
            "notes": [
                {"id": "1", "text": "Main user entity", "type": "Information"}
            ],
            "connections": [
                {"id": "1", "targetClass": "Profile", "relationship": "composition"}
            ]
        },
        {
            "id": "2", 
            "name": "Profile",
            "attributes": [
                {"id": "1", "name": "firstName", "type": "String", "visibility": "private"},
                {"id": "2", "name": "lastName", "type": "String", "visibility": "private"},
                {"id": "3", "name": "avatar", "type": "Image", "visibility": "private"}
            ],
            "operations": [
                {"id": "1", "name": "getFullName()", "visibility": "public"},
                {"id": "2", "name": "updateAvatar(Image)", "visibility": "public"}
            ],
            "notes": [
                {"id": "1", "text": "User profile details", "type": "Standard"}
            ],
            "connections": []
        },
        {
            "id": "3",
            "name": "AdminUser", 
            "attributes": [
                {"id": "1", "name": "permissions", "type": "List<String>", "visibility": "private"}
            ],
            "operations": [
                {"id": "1", "name": "grantPermission(String)", "visibility": "public"},
                {"id": "2", "name": "revokePermission(String)", "visibility": "public"}
            ],
            "notes": [],
            "connections": [
                {"id": "1", "targetClass": "User", "relationship": "inheritance"}
            ]
        }
    ]
    
    styling_options = {
        "outline_color": "#3b82f6",
        "outline_width": 2,
        "image_width": 1200,
        "image_height": 800
    }
    
    # Test 1: Validate classes
    print("\n1. Testing class validation...")
    try:
        response = requests.post(f"{BASE_URL}/api/validate-classes", 
                               json={"classes": sample_classes})
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Validation successful: {result['valid']}")
            if result.get('errors'):
                print(f"  Errors: {result['errors']}")
            if result.get('warnings'):
                print(f"  Warnings: {result['warnings']}")
        else:
            print(f"✗ Validation failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Validation error: {e}")
    
    # Test 2: Generate diagram
    print("\n2. Testing diagram generation...")
    try:
        response = requests.post(f"{BASE_URL}/api/generate-diagram", 
                               json={"classes": sample_classes, "styling": styling_options})
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✓ Diagram generated successfully!")
                print(f"  Diagram ID: {result['diagram_id']}")
                print(f"  Download URL: {result['download_url']}")
                
                # Test downloading the diagram
                download_response = requests.get(f"{BASE_URL}{result['download_url']}")
                if download_response.status_code == 200:
                    with open("test_generated_diagram.png", "wb") as f:
                        f.write(download_response.content)
                    print("  ✓ Diagram downloaded successfully as 'test_generated_diagram.png'")
                else:
                    print(f"  ✗ Download failed: {download_response.status_code}")
            else:
                print(f"✗ Diagram generation failed: {result['error']}")
        else:
            print(f"✗ Diagram generation failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Diagram generation error: {e}")
    
    # Test 3: Export PlantUML
    print("\n3. Testing PlantUML export...")
    try:
        response = requests.post(f"{BASE_URL}/api/export-plantuml", 
                               json={"classes": sample_classes})
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ PlantUML export successful!")
                with open("test_diagram.puml", "w") as f:
                    f.write(result['plantuml_code'])
                print("  ✓ PlantUML code saved as 'test_diagram.puml'")
                print(f"  Preview:\n{result['plantuml_code'][:200]}...")
            else:
                print(f"✗ PlantUML export failed: {result['error']}")
        else:
            print(f"✗ PlantUML export failed: {response.status_code}")
    except Exception as e:
        print(f"✗ PlantUML export error: {e}")
    
    # Test 4: Preview single class
    print("\n4. Testing class preview...")
    try:
        response = requests.post(f"{BASE_URL}/api/preview-class", 
                               json={"classData": sample_classes[0], "styling": styling_options})
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ Class preview generated successfully!")
                print(f"  Preview size: {result['width']}x{result['height']}")
                # The preview is base64 encoded image data
                print("  ✓ Preview data received (base64 encoded)")
            else:
                print(f"✗ Class preview failed: {result['error']}")
        else:
            print(f"✗ Class preview failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Class preview error: {e}")
    
    print("\n" + "=" * 40)
    print("API Testing Complete!")
    print("\nGenerated files:")
    print("- test_generated_diagram.png (UML diagram image)")
    print("- test_diagram.puml (PlantUML source code)")
    print("\nYou can now open http://127.0.0.1:5000 in your browser to use the web interface!")

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the Flask server is running on http://127.0.0.1:5000")
    print("Waiting 2 seconds before starting tests...")
    time.sleep(2)
    
    test_api_endpoints()