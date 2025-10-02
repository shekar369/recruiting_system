"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login with admin credentials"""
    print("=" * 60)
    print("Testing Admin Login")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "Admin123"
        }
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        print("\nLOGIN SUCCESSFUL!")
        return response.json()
    else:
        print("\nLOGIN FAILED!")
        return None


def test_me(token):
    """Test getting current user info"""
    print("\n" + "=" * 60)
    print("Testing Get Current User")
    print("=" * 60)

    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        print("\nGET CURRENT USER SUCCESSFUL!")
    else:
        print("\nGET CURRENT USER FAILED!")


def test_register():
    """Test user registration"""
    print("\n" + "=" * 60)
    print("Testing User Registration")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User",
            "role": "viewer"
        }
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 201:
        print("\nREGISTRATION SUCCESSFUL!")
    else:
        print("\nREGISTRATION FAILED!")


if __name__ == "__main__":
    # Test login
    tokens = test_login()

    if tokens:
        # Test get current user
        test_me(tokens['access_token'])

        # Test registration
        test_register()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
