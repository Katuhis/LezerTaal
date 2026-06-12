import pytest

from bson import ObjectId
from unittest.mock import patch

from models import TextResponse
from routers.texts import USER_ID

pytestmark = pytest.mark.asyncio


async def test_get_texts(client):
    with patch('routers.texts.db_get_texts') as mock_get:
        mock_get.return_value = []
        response = await client.get("/texts")
        assert response.status_code == 200
        assert response.json() == {"result": []}

async def test_get_texts_by_section(client):
    with patch('routers.texts.db_get_texts') as mock_get:
        mock_get.return_value = []
        section_id = str(ObjectId())
        response = await client.get(f"/texts?section_id={section_id}")
        assert response.status_code == 200
        mock_get.assert_called_with(USER_ID, section_id)

async def test_get_texts_by_id_success(client):
    with patch('routers.texts.db_get_text') as mock_get:
        text_id = str(ObjectId())
        mock_get.return_value = TextResponse(
            _id=text_id,
            title="title",
            content="content",
            language="en",
            created_at="2026-01-01"
        )
        response = await client.get(f"/texts/{text_id}")
        assert response.status_code == 200
        assert response.json().get("title") == "title"

async def test_get_texts_by_id_not_found(client):
    with patch('routers.texts.db_get_text') as mock_get:
        mock_get.side_effect = ValueError("Text not found")
        response = await client.get(f"/texts/{str(ObjectId())}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Text not found"}

async def test_create_texts(client):
    with patch('routers.texts.db_create_text') as mock_create:
        text_id = str(ObjectId())
        mock_create.return_value = text_id
        response = await client.post("/texts", json={"content": "content", "language": "nl"})
        assert response.status_code == 201
        assert response.json().get("result") == text_id

async def test_update_texts_success(client):
    with patch('routers.texts.db_update_text') as mock_update:
        mock_update.return_value = 1
        response = await client.put(f"/texts/{str(ObjectId())}", json={"title": "title", "content": "content", "language": "nl"})
        assert response.status_code == 200
        assert response.json().get("result") == 1

async def test_update_texts_not_found(client):
    with patch('routers.texts.db_update_text') as mock_update:
        mock_update.side_effect = ValueError("Text not found")
        response = await client.put(f"/texts/{str(ObjectId())}", json={"title": "title", "content": "content", "language": "nl"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Text not found"}

async def test_delete_texts_success(client):
    with patch('routers.texts.db_delete_text') as mock_delete:
        mock_delete.return_value = 1
        response = await client.delete(f"/texts/{str(ObjectId())}")
        assert response.status_code == 204

async def test_delete_texts_not_found(client):
    with patch('routers.texts.db_delete_text') as mock_delete:
        mock_delete.side_effect = ValueError("Text not found")
        response = await client.delete(f"/texts/{str(ObjectId())}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Text not found"}

async def test_delete_texts_by_section_success(client):
    with patch('routers.texts.db_delete_texts_by_section') as mock_delete:
        mock_delete.return_value = 2
        response = await client.delete(f"/texts/by-section/{str(ObjectId())}")
        assert response.status_code == 204