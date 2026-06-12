import pytest

from bson import ObjectId
from datetime import datetime
from services.sections import db_create_section, db_get_section, db_update_section, db_delete_section, db_get_sections_by_parent
from exceptions import SectionNotEmptyError

pytestmark = pytest.mark.asyncio


async def test_get_section_success(mock_db, seed):
    section_id = seed["sections"][0]

    result = await db_get_section(str(section_id))
    assert result.title == "Boek 1"


async def test_get_section_failure(mock_db, seed):
    with pytest.raises(ValueError):
        await db_get_section(str(ObjectId()))


async def test_db_get_sections_by_parent(mock_db, seed):
    user_id = seed["users"][0]
    parent_id = seed["sections"][0]

    await mock_db["sections"].insert_many([
        {
            "_id": ObjectId(),
            "title": "Boek 1 Hoofdstuk 1",
            "parent_id": parent_id,
            "user_id": user_id,
            "created_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "title": "Boek 1 Hoofdstuk 2",
            "parent_id": parent_id,
            "user_id": user_id,
            "created_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "title": "Boek 1 Hoofdstuk 3",
            "parent_id": parent_id,
            "user_id": user_id,
            "created_at": datetime.now()
        },
    ])

    result = await db_get_sections_by_parent(user_id=user_id, parent_id=parent_id)
    assert len(result) == 3
    assert result[0].title == "Boek 1 Hoofdstuk 1"

    result = await db_get_sections_by_parent(user_id=user_id)
    assert len(result) == 2


async def test_create_section_success(mock_db, seed):
    user_id = seed["users"][0]
    parent_id = seed["sections"][0]

    result = await db_create_section(
        title="title",
        user_id=str(user_id),
        parent_id=str(parent_id),
    )

    saved = await mock_db["sections"].find_one({"_id": ObjectId(result)})
    assert saved is not None
    assert saved["title"] == "title"
    assert saved["user_id"] == user_id
    assert saved["parent_id"] == parent_id


async def test_update_section_success(mock_db, seed):
    user_id = seed["users"][0]
    parent_id = seed["sections"][0]
    section_id = ObjectId()

    await mock_db["sections"].insert_one({
        "_id": section_id,
        "title": "old title",
        "parent_id": None,
        "user_id": user_id,
        "created_at": datetime.now()
    })

    result = await db_update_section(
        str(section_id),
        title="new title",
        parent_id=str(parent_id),
    )
    assert result == 1

    saved = await mock_db["sections"].find_one({"_id": section_id})
    assert saved["title"] == "new title"
    assert saved["parent_id"] == parent_id


async def test_update_section_failure(mock_db, seed):
    with pytest.raises(ValueError):
        await db_update_section(str(ObjectId()), title="new title")


async def test_delete_section_success(mock_db, seed):
    user_id = seed["users"][0]
    section_id = ObjectId()

    await mock_db["sections"].insert_one({
        "_id": section_id,
        "title": "title",
        "parent_id": None,
        "user_id": user_id,
        "created_at": datetime.now()
    })

    result = await db_delete_section(str(section_id))
    assert result == 1

    saved = await mock_db["sections"].find_one({"_id": section_id})
    assert saved is None


async def test_delete_section_has_children(mock_db, seed):
    user_id = seed["users"][0]
    parent_id = seed["sections"][0]
    section_id = ObjectId()

    await mock_db["sections"].insert_one({
        "_id": section_id,
        "title": "title",
        "parent_id": parent_id,
        "user_id": user_id,
        "created_at": datetime.now()
    })

    with pytest.raises(SectionNotEmptyError):
        await db_delete_section(str(parent_id))

async def test_delete_section_has_texts(mock_db, seed):
    user_id = seed["users"][0]
    section_id = seed["sections"][0]

    await mock_db["texts"].insert_one({
        "_id": ObjectId(),
        "title": "title",
        "content": "content",
        "language": "language",
        "user_id": user_id,
        "section_id": section_id,
        "created_at": datetime.now(),
    })

    with pytest.raises(SectionNotEmptyError):
        await db_delete_section(str(section_id))

async def test_delete_section_not_found(mock_db, seed):
    with pytest.raises(ValueError):
        await db_delete_section(str(ObjectId()))
