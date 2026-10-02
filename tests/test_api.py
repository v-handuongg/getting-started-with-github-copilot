from fastapi.testclient import TestClient

from src.app import activities


CHESS_SIGNUP_URL = "/activities/Chess%20Club/signup"


def test_root_redirects_to_static_index(client: TestClient):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client: TestClient):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"] == {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    }


def test_signup_and_unregister_round_trip(client: TestClient):
    email = "new.student@mergington.edu"

    signup_response = client.post(CHESS_SIGNUP_URL, params={"email": email})

    assert signup_response.status_code == 200
    assert signup_response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]
    assert email in client.get("/activities").json()["Chess Club"]["participants"]

    unregister_response = client.delete(CHESS_SIGNUP_URL, params={"email": email})

    assert unregister_response.status_code == 200
    assert unregister_response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in activities["Chess Club"]["participants"]
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client: TestClient):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_existing_participant(client: TestClient):
    response = client.post(
        CHESS_SIGNUP_URL,
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_rejects_unknown_activity(client: TestClient):
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_missing_participant(client: TestClient):
    response = client.delete(
        CHESS_SIGNUP_URL,
        params={"email": "not.registered@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }