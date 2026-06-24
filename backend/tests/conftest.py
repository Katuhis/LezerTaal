from datetime import datetime

import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient
from unittest.mock import patch
from bson import ObjectId

from main import app
from services.auth import get_current_user

app.dependency_overrides[get_current_user] = lambda: "6a0c644e3ad7680112699251"

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["lezertaal_test"]
    with (
        patch("services.texts.texts_collection", db["texts"]),
        patch("services.sections.sections_collection", db["sections"]),
        patch("services.sections.texts_collection", db["texts"]),
        patch("services.users.users_collection", db["users"]),
    ):
        yield db

@pytest_asyncio.fixture
async def seed(mock_db):
    user_ids = [ObjectId(), ObjectId()]
    await mock_db["users"].insert_many([
        {"_id": user_ids[0], "email": "anna@test.nl", "language": "ru"},
        {"_id": user_ids[1], "email": "bram@test.nl", "language": "ru"},
    ])

    section_ids = [ObjectId(), ObjectId()]
    await mock_db["sections"].insert_many([
        {
            "_id": section_ids[0],
            "title": "Boek 1",
            "parent_id": None,
            "user_id": user_ids[0],
            "created_at": datetime.now()
        },
        {
            "_id": section_ids[1],
            "title": "Eten",
            "parent_id": None,
            "user_id": user_ids[0],
            "created_at": datetime.now()
        },
    ])

    return {"users": user_ids, "sections": section_ids}