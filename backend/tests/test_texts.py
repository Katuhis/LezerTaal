import datetime
from unittest.mock import patch

import pytest

from services.texts import create_text, get_text, delete_text, update_text
from bson import ObjectId


def test_create_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.insert_one.return_value.inserted_id = "some_id"
        result = create_text(
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
            'created_at': datetime.datetime.now()
        }
        result = get_text(str(ObjectId()))
        assert result['title'] == "title"

def test_get_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.find_one.return_value = None
        with pytest.raises(ValueError):
            get_text(str(ObjectId()))

def test_delete_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.delete_one.return_value.deleted_count = 1
        result = delete_text(str(ObjectId()))
        assert result == 1

def test_delete_text_failure():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.delete_one.return_value.deleted_count = 0
        with pytest.raises(ValueError):
            delete_text(str(ObjectId()))

def test_update_text_success():
    with patch('services.texts.texts_collection') as mock_collection:
        mock_collection.update_one.return_value.modified_count = 1
        result = update_text(
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
            update_text(
                str(ObjectId()),
                'title',
                'language',
                str(ObjectId()),
            )