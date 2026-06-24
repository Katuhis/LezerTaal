from fastapi import APIRouter, Body, HTTPException

from services.users import db_create_user, db_get_user_by_email
from models import UserCreate, UserLogin
from services.utils import verify_password
from services.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", status_code=201)
async def register(user: UserCreate=Body(...)):
    try:
        await db_create_user(user.email, user.password, user.language)
        return {"message": "User created successfully!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Email {user.email} already exists!")

@router.post("/login", status_code=200)
async def login(user: UserLogin = Body(...)):
    try:
        search_user = await db_get_user_by_email(user.email)
        if search_user is None:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        is_password_correct = verify_password(user.password, search_user["hashed_password"])
        if not is_password_correct:
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        user_token = create_access_token(user.email)
        return {"access_token": user_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Incorrect email or password")