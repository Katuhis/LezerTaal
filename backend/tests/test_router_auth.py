from unittest.mock import patch

import pytest
from bson import ObjectId

from models import Language

pytestmark = pytest.mark.asyncio

async def test_register_success(client):
    with patch('routers.auth.db_create_user') as mock_register:
        mock_register.return_value = str(ObjectId())
        email = "test@test.nl"
        password = "1234"
        language = Language.NL
        response = await client.post("/auth/register", json={"email": email, "password": password, "language": language})
        assert response.status_code == 201
        mock_register.assert_called_with(email, password, language)

async def test_register_failure(client):
    with patch('routers.auth.db_create_user') as mock_register:
        email = "test@test.nl"
        password = "1234"
        language = Language.NL
        mock_register.side_effect = ValueError(f"Email {email} already exists.")
        response = await client.post("/auth/register", json={"email": email, "password": password, "language": language})
        assert response.status_code == 400

async def test_login_success(client):
    with patch('routers.auth.db_get_user_by_email') as mock_get, \
            patch('routers.auth.verify_password') as mock_verify, \
            patch('routers.auth.create_access_token') as mock_token:
        mock_get.return_value = {"email": "test@test.nl", "hashed_password": "hash"}
        mock_verify.return_value = True
        mock_token.return_value = "user_token"
        response = await client.post("/auth/login", json={"email": "test@test.nl", "password": "1234"})
        assert response.status_code == 200
        assert response.json()["access_token"] == "user_token"

async def test_login_failure(client):
    with patch('routers.auth.db_get_user_by_email') as mock_get, patch('routers.auth.verify_password') as mock_verify:
        mock_get.return_value = {"email": "test@test.nl", "hashed_password": "hash"}
        mock_verify.return_value = False
        response = await client.post("/auth/login", json={"email": "test@test.nl", "password": "1234"})
        assert response.status_code == 401