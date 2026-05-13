from datetime import datetime
from bson import ObjectId
from services.database import sections_collection, texts_collection


def create_section(
        title: str,
        user_id: str,
        parent_id: str = None,
):
    created_at = datetime.now()

    section = {
        'title': title,
        'user_id': ObjectId(user_id),
        'parent_id': ObjectId(parent_id) if parent_id else None,
        'created_at': created_at,
    }

    result = sections_collection.insert_one(section)
    return result.inserted_id

def get_section(section_id: str):
    section = sections_collection.find_one({'_id': ObjectId(section_id)})

    if section is None:
        raise ValueError(f"Section {section_id} was not found.")

    return section

def get_texts_from_section(section_id: str):
    texts = list(texts_collection.find({'section_id': ObjectId(section_id)}))

    return texts

def update_section(
        section_id: str,
        title: str,
        parent_id: str = None,
):
    section = {
        'title': title,
    }
    if parent_id:
        section['parent_id'] = ObjectId(parent_id)

    result = sections_collection.update_one({'_id': ObjectId(section_id)}, {'$set': section})
    if result.modified_count == 0:
        raise ValueError(f"Section {section_id} was not found.")

    return result.modified_count

def delete_section(section_id: str):
    inner_sections = sections_collection.find_one({'parent_id': ObjectId(section_id)})

    if inner_sections is not None:
        raise ValueError(f"Section {section_id} has inner sections.")

    texts_collection.delete_many({'section_id': ObjectId(section_id)})

    result = sections_collection.delete_one({'_id': ObjectId(section_id)})
    if result.deleted_count == 0:
        raise ValueError(f"Section {section_id} was not found.")
    return result.deleted_count
