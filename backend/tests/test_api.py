from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Chatbot API is online"}

@patch("app.api.chat.chat_endpoint")
def test_chat_endpoint_success(mock_generate):
    """Test a valid chat request returns the expected structure."""

    mock_generate.return_value = "Hello! I am a mocked AI response."
    
    payload = {
        "user_input": "Hello, bot!",
        "session_id": "test-session-123"
    }
    response = client.post("/api/v1/chat", json=payload)
    

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "source" in data
    assert isinstance(data["response"], str) == True
    assert isinstance(data["source"], str) == True

def test_chat_endpoint_invalid_json():
    """Test that missing required fields returns a 422 Unprocessable Entity."""
    # Missing 'user_input'
    payload = {"session_id": "only-session"}
    response = client.post("/api/v1/chat", json=payload)
    
    assert response.status_code == 422
    # Verify the error message points to the missing field
    assert response.json()["detail"][0]["loc"] == ["body", "user_input"]

def test_chat_endpoint_wrong_method():
    """Test that using GET on a POST endpoint returns 405 Method Not Allowed."""
    response = client.get("/api/v1/chat")
    assert response.status_code == 405
