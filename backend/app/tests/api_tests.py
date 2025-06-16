from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_surveys():
    response = client.get("/surveys")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_get_survey():
    survey_name = "survey_name"
    response = client.get(f"/surveys/{survey_name}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_get_question():
    question_id = "question_id"
    response = client.get(f"/questions/{question_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_upload_csv():
    with open("path/to/test.csv", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"