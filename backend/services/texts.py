from datetime import datetime
from services.database import texts_collection
from bson import ObjectId


def create_text(
        title: str,
        content: str,
        language: str,
        user_id: str,
        section_id: str = None,
):
    created_at = datetime.now()

    text = {
        'title': title,
        'content': content,
        'language': language,
        'user_id': ObjectId(user_id),
        'section_id': ObjectId(section_id) if section_id else None,
        'created_at': created_at,
    }

    result = texts_collection.insert_one(text)
    return result.inserted_id

def get_text(text_id: str):
    result = texts_collection.find_one({'_id': ObjectId(text_id)})
    if result is None:
        raise ValueError(f"Text {text_id} was not found.")
    return result

def get_texts(user_id: str):
    return list(texts_collection.find({'user_id': ObjectId(user_id)}))

def delete_text(text_id: str):
    result = texts_collection.delete_one({'_id': ObjectId(text_id)})
    if result.deleted_count == 0:
        raise ValueError(f"Text {text_id} was not found.")
    return result.deleted_count

def update_text(
        text_id: str,
        title: str = None,
        language: str = None,
        section_id: str = None,
):
    text = {}
    if title:
        text['title'] = title
    if language:
        text['language'] = language
    if section_id:
        text['section_id'] = ObjectId(section_id)

    result = texts_collection.update_one({'_id': ObjectId(text_id)}, {'$set': text})
    if result.modified_count == 0:
        raise ValueError(f"Text {text_id} was not found.")

    return result.modified_count
