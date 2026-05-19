import pytest

from datetime import datetime
from unittest.mock import patch
from services.texts import db_create_text, db_get_text, db_delete_text, db_update_text
from bson import ObjectId


def test_create_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.insert_one.return_value.inserted_id = "some_id"
        result = db_create_text(
            title='title',
            content='content',
            language='language',
            user_id=str(ObjectId()),
            section_id=str(ObjectId())
        )
        assert result == "some_id"

def test_get_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.find_one.return_value = {
            "_id": ObjectId(),
            'title': 'title',
            'content': 'content',
            'language': 'language',
            'user_id': ObjectId(),
            'created_at': datetime.now()
        }
        result = db_get_text(str(ObjectId()))
        assert result['title'] == "title"

def test_get_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.find_one.return_value = None
        with pytest.raises(ValueError):
            db_get_text(str(ObjectId()))

def test_delete_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.delete_one.return_value.deleted_count = 1
        result = db_delete_text(str(ObjectId()))
        assert result == 1

def test_delete_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.delete_one.return_value.deleted_count = 0
        with pytest.raises(ValueError):
            db_delete_text(str(ObjectId()))

def test_update_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.update_one.return_value.modified_count = 1
        result = db_update_text(
            str(ObjectId()),
            'title',
            'language',
            str(ObjectId()),
        )
        assert result == 1

def test_update_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.update_one.return_value.modified_count = 0
        with pytest.raises(ValueError):
            db_update_text(
                str(ObjectId()),
                'title',
                'language',
                str(ObjectId()),
            )