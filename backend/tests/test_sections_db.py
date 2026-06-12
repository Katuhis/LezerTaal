import pytest

from bson import ObjectId
from unittest.mock import patch
from services.sections import create_section, get_section, get_texts_from_section, update_section, delete_section


def test_create_section_success():
    with patch('services.sections.sections_collection') as mock_collection:
        mock_collection.insert_one.return_value.inserted_id = "some_id"
        result = create_section(
            title='title',
            user_id=str(ObjectId()),
            parent_id=str(ObjectId())
        )
        assert result == "some_id"

def get_section_success():
    with patch('services.sections.sections_collection') as mock_collection:
        mock_collection.find_one.return_value = {
            "_id": ObjectId(),
            'title': 'title',
            'user_id': ObjectId(),
            'parent_id': ObjectId()
        }
        result = get_section(str(ObjectId()))
        assert result['title'] == "title"

def get_section_failure():
    with patch('services.sections.sections_collection') as mock_collection:
        mock_collection.find_one.return_value = None
        with pytest.raises(ValueError):
            get_section(str(ObjectId()))

def test_get_texts_from_section_success():
    with patch('services.sections.texts_collection') as mock_collection:
        mock_collection.find.return_value = [1, 2, 3]
        result = get_texts_from_section(str(ObjectId()))
        assert result == [1, 2, 3]

def update_section_success():
    with patch('services.sections.sections_collection') as mock_collection:
        mock_collection.update_one.return_value.modified_count = 1
        result = update_section(
            str(ObjectId()),
            'title',
            str(ObjectId()),
        )
        assert result == 1

def test_update_section_failure():
    with patch('services.sections.sections_collection') as mock_collection:
        mock_collection.update_one.return_value.modified_count = 0
        with pytest.raises(ValueError):
            update_section(
                str(ObjectId()),
                'title',
                str(ObjectId()),
            )

def test_delete_section_success():
    with patch('services.sections.sections_collection') as mock_sections:
        mock_sections.find_one.return_value = None
        with patch('services.sections.texts_collection') as mock_texts:
            mock_sections.delete_one.return_value.deleted_count = 1
            result = delete_section(str(ObjectId()))
            assert mock_texts.delete_many.called
            assert result == 1

def test_delete_section_has_children():
    with patch('services.sections.sections_collection') as mock_sections:
        mock_sections.find_one.return_value = {
            "_id": ObjectId(),
            'title': 'title',
            'user_id': ObjectId(),
            'parent_id': ObjectId()
        }
        with patch('services.sections.texts_collection') as mock_texts:
            with pytest.raises(ValueError):
                delete_section(str(ObjectId()))

def test_delete_section_not_found():
    with patch('services.sections.sections_collection') as mock_sections:
        mock_sections.delete_one.return_value.deleted_count = 0
        with pytest.raises(ValueError):
            delete_section(str(ObjectId()))