import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # First, get initial participants
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Basketball Team"]["participants"])
    
    # Sign up
    response = client.post("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Check updated
    response = client.get("/activities")
    data = response.json()
    assert len(data["Basketball Team"]["participants"]) == initial_count + 1
    assert "test@mergington.edu" in data["Basketball Team"]["participants"]

def test_signup_already_signed_up():
    # Sign up first
    client.post("/activities/Basketball%20Team/signup?email=duplicate@mergington.edu")
    
    # Try again
    response = client.post("/activities/Basketball%20Team/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_success():
    # Sign up first
    client.post("/activities/Swimming%20Club/signup?email=unregister@mergington.edu")
    
    # Unregister
    response = client.delete("/activities/Swimming%20Club/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    
    # Check removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@mergington.edu" not in data["Swimming Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess%20Club/unregister?email=notsigned@mergington.edu")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]