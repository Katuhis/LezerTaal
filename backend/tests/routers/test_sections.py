import pytest

from bson import ObjectId
from unittest.mock import patch

from exceptions import SectionNotEmptyError

TEST_USER_ID = "6a0c644e3ad7680112699251"

pytestmark = pytest.mark.asyncio


async def test_get_sections(client):
    with patch('routers.sections.db_get_sections_by_parent') as mock_get:
        mock_get.return_value = []
        response = await client.get("/sections")
        assert response.status_code == 200
        assert response.json() == {"result": []}
        mock_get.assert_called_with(TEST_USER_ID)


async def test_get_section_success(client):
    with patch('routers.sections.db_get_section') as mock_get:
        section_id = str(ObjectId())
        mock_get.return_value = {"title": "title"}
        response = await client.get(f"/sections/{section_id}")
        assert response.status_code == 200
        assert response.json()["result"]["title"] == "title"


async def test_get_section_not_found(client):
    with patch('routers.sections.db_get_section') as mock_get:
        mock_get.side_effect = ValueError("Section not found")
        response = await client.get(f"/sections/{str(ObjectId())}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Section not found"}


async def test_get_section_children(client):
    with patch('routers.sections.db_get_sections_by_parent') as mock_get:
        mock_get.return_value = []
        section_id = str(ObjectId())
        response = await client.get(f"/sections/{section_id}/children")
        assert response.status_code == 200
        mock_get.assert_called_with(TEST_USER_ID, section_id)


async def test_create_section(client):
    with patch('routers.sections.db_create_section') as mock_create:
        section_id = str(ObjectId())
        mock_create.return_value = section_id
        response = await client.post("/sections", json={"title": "title"})
        assert response.status_code == 201
        assert response.json().get("result") == section_id


async def test_update_section_success(client):
    with patch('routers.sections.db_update_section') as mock_update:
        mock_update.return_value = 1
        response = await client.put(f"/sections/{str(ObjectId())}", json={"title": "new title"})
        assert response.status_code == 200
        assert response.json().get("result") == 1


async def test_update_section_not_found(client):
    with patch('routers.sections.db_update_section') as mock_update:
        mock_update.side_effect = ValueError("Section not found")
        response = await client.put(f"/sections/{str(ObjectId())}", json={"title": "new title"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Section not found"}


async def test_delete_section_success(client):
    with patch('routers.sections.db_delete_section') as mock_delete:
        mock_delete.return_value = 1
        response = await client.delete(f"/sections/{str(ObjectId())}")
        assert response.status_code == 204


async def test_delete_section_not_empty(client):
    with patch('routers.sections.db_delete_section') as mock_delete:
        mock_delete.side_effect = SectionNotEmptyError("Section is not empty")
        response = await client.delete(f"/sections/{str(ObjectId())}")
        assert response.status_code == 400
        assert response.json() == {"detail": "Section is not empty"}


async def test_delete_section_not_found(client):
    with patch('routers.sections.db_delete_section') as mock_delete:
        mock_delete.side_effect = ValueError("Section not found")
        response = await client.delete(f"/sections/{str(ObjectId())}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Section not found"}