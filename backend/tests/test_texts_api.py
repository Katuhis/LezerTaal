from datetime import datetime

from bson import ObjectId
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from models import TextResponse

client = TestClient(app)

def test_get_texts():
    with patch('routers.texts.db_get_texts') as mock_get:
        mock_get.return_value = []
        response = client.get("/texts")
        assert response.status_code == 200
        assert response.json() == {"result": []}

def test_get_texts_by_id_success():
    with patch('routers.texts.db_get_text') as mock_get:
        text_id = str(ObjectId())
        mock_get.return_value = TextResponse(
            _id=text_id,
            title="title",
            content="content",
            language="en",
            user_id=text_id,
            created_at="2026-01-01"
        )
        response = client.get("/texts/{text_id}")
        assert response.status_code == 200
        assert response.json().get("title") == "title"

def test_get_texts_by_id_not_found():
    with patch('routers.texts.db_get_text') as mock_get:
        mock_get.side_effect = ValueError("Text not found")
        response = client.get("/texts/{text_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Text not found"}

def test_create_texts():
    with patch('routers.texts.db_create_text') as mock_create:
        text_id = str(ObjectId())
        mock_create.return_value = text_id
        response = client.post("/texts", json={"content": "content", "language": "nl"})
        assert response.status_code == 201
        assert response.json().get("result") == text_id

def test_update_texts_success():
    with patch('routers.texts.db_update_text') as mock_update:
        mock_update.return_value = 1
        response = client.put("/texts/{text_id}", json={"title": "title", "content": "content", "language": "nl"})
        assert response.status_code == 200
        assert response.json().get("result") == 1

def test_update_texts_not_found():
    with patch('routers.texts.db_update_text') as mock_update:
        mock_update.side_effect = ValueError("Text not found")
        response = client.put("/texts/{text_id}", json={"title": "title", "content": "content", "language": "nl"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Text not found"}

def test_delete_texts_success():
    with patch('routers.texts.db_delete_text') as mock_delete:
        mock_delete.return_value = 0
        response = client.delete("/texts/{text_id}")
        assert response.status_code == 204

def test_delete_texts_not_found():
    with patch('routers.texts.db_delete_text') as mock_delete:
        mock_delete.side_effect = ValueError("Text not found")
        response = client.delete("/texts/{text_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Text not found"}