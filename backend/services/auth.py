from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from services.users import db_get_user_by_email

security = HTTPBearer()

def create_access_token(email: str) -> str:
    exp = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({'sub': email, 'exp': exp}, SECRET_KEY, algorithm='HS256')
    return token

def decode_access_token(token: str) -> str:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded['sub']
    except JWTError as e:
        raise ValueError('Invalid token')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        token_email = decode_access_token(token)
        user = await db_get_user_by_email(token_email)
        if user is None:
            raise HTTPException(status_code=401, detail='Invalid token')

        return str(user["_id"])
    except ValueError as e:
        raise HTTPException(status_code=401, detail='Invalid token')