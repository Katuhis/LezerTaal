import pytest

from bson import ObjectId

from models import Language
from services.users import db_get_user_by_email, db_create_user

pytestmark = pytest.mark.asyncio

async def test_get_user_by_email(mock_db, seed):
    await mock_db["users"].insert_one({"_id": ObjectId(), "email": "test@test.nl", "language": "ru"})

    result_found = await db_get_user_by_email("test@test.nl")
    assert result_found is not None
    assert result_found["email"] == "test@test.nl"

    result_not_found = await db_get_user_by_email("test1@test.nl")
    assert result_not_found is None

async def test_create_user_success(mock_db, seed):
    result = await db_create_user(
        email="test@test.nl",
        password="1234",
        language=Language.NL
    )

    saved = await mock_db["users"].find_one({"_id": ObjectId(result)})
    assert saved is not None
    assert saved["email"] == "test@test.nl"
    assert saved["language"] == Language.NL
    assert saved["hashed_password"] != "1234"
    assert saved["hashed_password"].startswith("$2b$")

async def test_create_user_fail(mock_db, seed):
    with pytest.raises(ValueError):
        await db_create_user(
            email="anna@test.nl",
            password="1234",
            language=Language.NL
        )
