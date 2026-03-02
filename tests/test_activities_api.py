from urllib.parse import quote


def activity_signup_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success(client):
    email = "new.student@mergington.edu"
    response = client.post(activity_signup_path("Chess Club"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_unknown_activity_returns_404(client):
    response = client.post(
        activity_signup_path("Unknown Activity"),
        params={"email": "someone@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_returns_409_with_message(client):
    existing_email = "michael@mergington.edu"
    response = client.post(activity_signup_path("Chess Club"), params={"email": existing_email})

    assert response.status_code == 409
    assert response.json() == {"message": "Participant already registered"}


def test_remove_signup_success(client):
    email = "temp.student@mergington.edu"
    client.post(activity_signup_path("Robotics Team"), params={"email": email})

    response = client.delete(activity_signup_path("Robotics Team"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Robotics Team"}

    activities = client.get("/activities").json()
    assert email not in activities["Robotics Team"]["participants"]


def test_remove_unknown_participant_returns_404(client):
    response = client.delete(
        activity_signup_path("Chess Club"),
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}


def test_remove_unknown_activity_returns_404(client):
    response = client.delete(
        activity_signup_path("Unknown Activity"),
        params={"email": "any@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_state_consistency_after_signup_and_remove(client):
    activity_name = "Science Club"
    email = "consistency@mergington.edu"

    initial = client.get("/activities").json()[activity_name]["participants"]
    assert email not in initial

    signup_response = client.post(activity_signup_path(activity_name), params={"email": email})
    assert signup_response.status_code == 200

    after_signup = client.get("/activities").json()[activity_name]["participants"]
    assert email in after_signup

    remove_response = client.delete(activity_signup_path(activity_name), params={"email": email})
    assert remove_response.status_code == 200

    after_remove = client.get("/activities").json()[activity_name]["participants"]
    assert email not in after_remove
