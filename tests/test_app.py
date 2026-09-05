from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_static_index_is_served(client):
    response = client.get("/static/index.html")

    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert activities["Chess Club"]["max_participants"] == 12
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    activity = quote("Chess Club", safe="")
    email = quote("new.student@mergington.edu", safe="")

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new.student@mergington.edu for Chess Club"
    }
    assert "new.student@mergington.edu" in client.get("/activities").json()[
        "Chess Club"
    ]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity = quote("Chess Club", safe="")
    email = quote("michael@mergington.edu", safe="")

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    activity = quote("Unknown Club", safe="")
    email = quote("student@mergington.edu", safe="")

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email(client):
    activity = quote("Chess Club", safe="")

    response = client.post(f"/activities/{activity}/signup")

    assert response.status_code == 422


def test_remove_participant(client):
    activity = quote("Chess Club", safe="")
    email = quote("michael@mergington.edu", safe="")

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in client.get("/activities").json()[
        "Chess Club"
    ]["participants"]


def test_remove_participant_rejects_unknown_activity(client):
    activity = quote("Unknown Club", safe="")
    email = quote("student@mergington.edu", safe="")

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_rejects_unknown_participant(client):
    activity = quote("Chess Club", safe="")
    email = quote("unknown@mergington.edu", safe="")

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"