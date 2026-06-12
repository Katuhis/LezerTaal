import pytest

from datetime import datetime
from services.texts import db_create_text, db_get_text, db_delete_text, db_update_text, db_get_texts, db_delete_texts_by_section
from bson import ObjectId


pytestmark = pytest.mark.asyncio


async def test_get_texts(mock_db, seed):
    user_id = seed["users"][0]
    section_id = seed["sections"][0]

    await mock_db["texts"].insert_many([
        {
            "_id": ObjectId(),
            "title": "In de sectie",
            "content": "content",
            "language": "nl",
            "user_id": user_id,
            "section_id": section_id,
            "created_at": datetime.now(),
        },
        {
            "_id": ObjectId(),
            "title": "Zonder sectie",
            "content": "content",
            "language": "nl",
            "user_id": user_id,
            "section_id": None,
            "created_at": datetime.now(),
        },
        {
            "_id": ObjectId(),
            "title": "Van een andere gebruiker",
            "content": "content",
            "language": "nl",
            "user_id": seed["users"][1],
            "section_id": None,
            "created_at": datetime.now(),
        },
    ])

    # тексты конкретной секции
    result = await db_get_texts(str(user_id), str(section_id))
    assert len(result) == 1
    assert result[0].title == "In de sectie"

    # тексты без секции ("корзина")
    result = await db_get_texts(str(user_id))
    assert len(result) == 1
    assert result[0].title == "Zonder sectie"

    # запись другого юзера не должна попасть в результат
    titles = [t.title for t in result]
    assert "Van een andere gebruiker" not in titles

async def test_get_text_success(mock_db, seed):
    user_id = seed["users"][0]
    text_id = ObjectId()

    await mock_db["texts"].insert_one({
        "_id": text_id,
        "title": "title",
        "content": "content",
        "language": "language",
        "user_id": user_id,
        "section_id": None,
        "created_at": datetime.now(),
    })

    result = await db_get_text(str(text_id))
    assert result.title == "title"

async def test_get_text_failure(mock_db, seed):
    with pytest.raises(ValueError):
        await db_get_text(str(ObjectId()))

async def test_create_text_success(mock_db, seed):
    user_id = seed["users"][0]
    section_id = seed["sections"][0]

    result = await db_create_text(
        title="title",
        content="content",
        language="language",
        user_id=str(user_id),
        section_id=str(section_id),
    )

    saved = await mock_db["texts"].find_one({"_id": ObjectId(result)})
    assert saved is not None
    assert saved["title"] == "title"
    assert saved["content"] == "content"
    assert saved["language"] == "language"
    assert saved["user_id"] == user_id
    assert saved["section_id"] == section_id


async def test_update_text_success(mock_db, seed):
    user_id = seed["users"][0]
    text_id = ObjectId()
    new_section_id = seed["sections"][1]

    await mock_db["texts"].insert_one({
        "_id": text_id,
        "title": "old title",
        "content": "content",
        "language": "old language",
        "user_id": user_id,
        "section_id": None,
        "created_at": datetime.now(),
    })

    result = await db_update_text(
        str(text_id),
        title="new title",
        language="new language",
        section_id=str(new_section_id)
    )
    assert result == 1

    saved = await mock_db["texts"].find_one({"_id": text_id})
    assert saved["title"] == "new title"
    assert saved["language"] == "new language"
    assert saved["section_id"] == new_section_id


async def test_update_text_failure(mock_db, seed):
    with pytest.raises(ValueError):
        await db_update_text(str(ObjectId()), title="new title")


async def test_delete_text_success(mock_db, seed):
    user_id = seed["users"][0]
    text_id = ObjectId()

    await mock_db["texts"].insert_one({
        "_id": text_id,
        "title": "title",
        "content": "content",
        "language": "language",
        "user_id": user_id,
        "section_id": None,
        "created_at": datetime.now(),
    })

    result = await db_delete_text(str(text_id))
    assert result == 1

    saved = await mock_db["texts"].find_one({"_id": text_id})
    assert saved is None


async def test_delete_text_failure(mock_db, seed):
    with pytest.raises(ValueError):
        await db_delete_text(str(ObjectId()))


async def test_delete_texts_by_section(mock_db, seed):
    user_id = seed["users"][0]
    section_id_0 = seed["sections"][0]
    section_id_1 = seed["sections"][1]

    await mock_db["texts"].insert_many([
        {
            "_id": ObjectId(),
            "title": "text 1",
            "content": "content",
            "language": "language",
            "user_id": user_id,
            "section_id": section_id_0,
            "created_at": datetime.now(),
        },
        {
            "_id": ObjectId(),
            "title": "text 2",
            "content": "content",
            "language": "language",
            "user_id": user_id,
            "section_id": section_id_0,
            "created_at": datetime.now(),
        },
        {
            "_id": ObjectId(),
            "title": "text 3",
            "content": "content",
            "language": "language",
            "user_id": user_id,
            "section_id": section_id_1,
            "created_at": datetime.now(),
        },
    ])

    result = await db_delete_texts_by_section(str(user_id), str(section_id_0))
    assert result == 2

    remaining = await mock_db["texts"].find({"user_id": user_id}).to_list()
    assert len(remaining) == 1
    assert remaining[0]["title"] == "text 3"