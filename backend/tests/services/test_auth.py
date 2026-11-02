import pytest

from services.auth import create_access_token, decode_access_token

def test_create_access_token():
    token = create_access_token("email")
    email = decode_access_token(token)
    assert email == "email"

def test_decode_invalid_token():
    with pytest.raises(ValueError):
        decode_access_token("invalid_token")