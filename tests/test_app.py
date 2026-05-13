import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_data

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities_data)
    yield
    activities_data.clear()
    activities_data.update(original_activities)


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_new_participant():
    email = "test@example.com"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for Chess Club" == data["message"]
    assert email in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_participant():
    email = "emma@mergington.edu"
    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_remove_participant():
    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities_data["Chess Club"]["participants"]


def test_remove_nonexistent_participant():
    email = "unknown@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"


def test_signup_missing_activity():
    email = "missing@example.com"
    response = client.post(
        "/activities/Nonexistent%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
