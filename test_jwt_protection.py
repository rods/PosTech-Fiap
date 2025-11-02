"""
Test script to demonstrate JWT protection on the create book endpoint.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_create_book_without_auth():
    """Test creating a book without authentication - should fail"""
    print("1. Testing create book without authentication...")
    
    book_data = {
        "id": 999,
        "title": "Test Book",
        "price": 29.99,
        "rating": 5,
        "availability": "In stock",
        "category": "Fiction"
    }
    
    response = requests.post(f"{BASE_URL}/books", json=book_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_login_and_create_book():
    """Test login and then create book with JWT token"""
    print("2. Testing login and create book with JWT...")
    
    # First, login to get JWT token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"   Token received: {token[:20]}...")
        
        # Now try to create book with token
        headers = {"Authorization": f"Bearer {token}"}
        book_data = {
            "id": 1000,
            "title": "Authenticated Book",
            "price": 39.99,
            "rating": 4,
            "availability": "In stock",
            "category": "Technology"
        }
        
        create_response = requests.post(f"{BASE_URL}/books", json=book_data, headers=headers)
        print(f"   Create Book Status: {create_response.status_code}")
        print(f"   Create Book Response: {create_response.json()}")
    else:
        print(f"   Login failed: {login_response.json()}")
    print()

def test_invalid_token():
    """Test creating book with invalid token"""
    print("3. Testing create book with invalid token...")
    
    headers = {"Authorization": "Bearer invalid_token_123"}
    book_data = {
        "id": 1001,
        "title": "Invalid Token Book",
        "price": 19.99,
        "rating": 3,
        "availability": "In stock",
        "category": "Mystery"
    }
    
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("JWT Protection Test for Create Book API")
    print("=" * 50)
    print()
    
    try:
        test_create_book_without_auth()
        test_login_and_create_book()
        test_invalid_token()
        
        print("Test completed!")
        print("\nNote: Make sure the FastAPI server is running on localhost:8000")
        print("Start server with: uvicorn app.main:app --reload")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on localhost:8000")
        print("Start with: uvicorn app.main:app --reload")