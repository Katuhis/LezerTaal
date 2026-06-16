from datetime import datetime

from services.database import users_collection
from models import Language
from services.utils import hash_password


async def db_get_user_by_email(email: str):
    result = await users_collection.find_one({'email': email})
    return result

async def db_create_user(
        email: str,
        password: str,
        language: Language
):
    if await db_get_user_by_email(email) is not None:
        raise ValueError(f"Email {email} already exists.")

    hashed_password = hash_password(password)

    created_at = datetime.now()

    user = {
        'email': email,
        'hashed_password': hashed_password,
        'language': language,
        'created_at': created_at,
    }

    result = await users_collection.insert_one(user)
    return result.inserted_id