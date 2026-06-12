from datetime import datetime
from typing import Optional

from bson import ObjectId

from exceptions import SectionNotEmptyError
from services.database import sections_collection, texts_collection
from services.utils import serialize_text, serialize_section


async def db_get_section(section_id: str):
    section = await sections_collection.find_one({'_id': ObjectId(section_id)})

    if section is None:
        raise ValueError(f"Section {section_id} was not found.")

    return serialize_section(section)

async def db_get_sections_by_parent(user_id: str, parent_id: Optional[str] = None):
    if parent_id:
        sections = await sections_collection.find({'parent_id': ObjectId(parent_id)}).to_list(None)
    else:
        sections = await sections_collection.find({'user_id': ObjectId(user_id), 'parent_id': None}).to_list(None)

    return [serialize_section(section) for section in sections]

async def db_create_section(
        title: str,
        user_id: str,
        parent_id: Optional[str] = None,
):
    created_at = datetime.now()

    section = {
        'title': title,
        'user_id': ObjectId(user_id),
        'parent_id': ObjectId(parent_id) if parent_id else None,
        'created_at': created_at,
    }

    result = await sections_collection.insert_one(section)
    return result.inserted_id

async def db_update_section(
        section_id: str,
        title: str,
        parent_id: Optional[str] = None,
):
    section = {
        'title': title,
    }
    if parent_id:
        section['parent_id'] = ObjectId(parent_id)

    result = await sections_collection.update_one({'_id': ObjectId(section_id)}, {'$set': section})
    if result.modified_count == 0:
        raise ValueError(f"Section {section_id} was not found.")

    return result.modified_count

async def db_delete_section(section_id: str):
    inner_sections = await sections_collection.find_one({'parent_id': ObjectId(section_id)})

    if inner_sections is not None:
        raise SectionNotEmptyError(f"Section {section_id} has inner sections.")

    inner_texts = await texts_collection.find_one({'section_id': ObjectId(section_id)})

    if inner_texts is not None:
        raise SectionNotEmptyError(f"Section {section_id} has inner texts.")

    result = await sections_collection.delete_one({'_id': ObjectId(section_id)})
    if result.deleted_count == 0:
        raise ValueError(f"Section {section_id} was not found.")
    return result.deleted_count
