from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = activities["Chess Club"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"] == expected_activity


def test_signup_adds_student_to_activity():
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_duplicate_signup_returns_bad_request():
    # Arrange
    email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_without_email_returns_validation_error():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_student_from_activity():
    # Arrange
    email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_from_unknown_activity_returns_not_found():
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_non_participant_returns_not_found():
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }