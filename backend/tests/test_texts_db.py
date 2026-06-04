import pytest

from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from services.texts import db_create_text, db_get_text, db_delete_text, db_update_text, db_get_texts
from bson import ObjectId


pytestmark = pytest.mark.asyncio


async def test_create_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="some_id"))
        result = await db_create_text(
            title='title',
            content='content',
            language='language',
            user_id=str(ObjectId()),
            section_id=str(ObjectId())
        )
        assert result == "some_id"

async def test_get_texts():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[{
            "_id": ObjectId(),
            'title': 'title',
            'content': 'content',
            'language': 'language',
            'user_id': ObjectId(),
            'created_at': datetime.now(),
            'section_id': ObjectId(),
        }])
        mock_collection.find.return_value = mock_cursor
        result = await db_get_texts(str(ObjectId()))
        assert len(result) == 1
        assert result[0].title == "title"

async def test_get_text_success():
    with (patch('services.texts.texts_collection') as mock_collection):
        mock_collection.find_one = AsyncMock(return_value={
            "_id": ObjectId(),
            'title': 'title',
            'content': 'content',
            'language': 'language',
            'user_id': ObjectId(),
            'created_at': datetime.now(),
            'section_id': ObjectId(),
        })
        result = await db_get_text(str(ObjectId()))
        assert result.title == "title"

async def test_get_text_failure():
    with (patch('services.texts.texts_collection') as mock_collection):
        mock_collection.find_one = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await db_get_text(str(ObjectId()))

async def test_delete_text_success():
    with (patch('services.texts.texts_collection') as mock_collection):
        mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        result = await db_delete_text(str(ObjectId()))
        assert result == 1

async def test_delete_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=0))
        with pytest.raises(ValueError):
            await db_delete_text(str(ObjectId()))

async def test_update_text_success():
    with (patch('services.texts.texts_collection') as mock_collection):
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
        result = await db_update_text(
            str(ObjectId()),
            'title',
            'language',
            str(ObjectId()),
        )
        assert result == 1

async def test_update_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=0))
        with pytest.raises(ValueError):
            await db_update_text(
                str(ObjectId()),
                'title',
                'language',
                str(ObjectId()),
            )