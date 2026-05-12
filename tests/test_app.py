from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newtester@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert email in data["message"]
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    client.post(signup_url, params={"email": email})

    # Act
    response = client.post(signup_url, params={"email": email})
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Email already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "missing@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"


def test_delete_participant_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "delete-me@mergington.edu"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"
    delete_url = f"/activities/{quote(activity_name, safe='')}/participants"

    client.post(signup_url, params={"email": email})

    # Act
    response = client.delete(delete_url, params={"email": email})
    delete_data = response.json()

    # Assert
    assert response.status_code == 200
    assert email in delete_data["message"]
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_delete_missing_participant_returns_404():
    # Arrange
    activity_name = "Programming Class"
    missing_email = "not-there@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": missing_email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Participant not found"


def test_delete_missing_activity_returns_404():
    # Arrange
    activity_name = "No Such Activity"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"
