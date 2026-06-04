from fastapi import APIRouter, Body, HTTPException

from models import TextCreate
from services.texts import db_create_text, db_get_texts, db_get_text, db_update_text, db_delete_text

USER_ID='6a0c644e3ad7680112699251'

router = APIRouter(prefix="/texts", tags=["texts"])

@router.get("/")
async def get_texts():
    texts = await db_get_texts(USER_ID)
    return {"result": texts}

@router.post("/", status_code=201)
async def post_text(text: TextCreate = Body(...)):
    if text.title is None:
        text.title = ' '.join(text.content.split()[:5])

    result = await db_create_text(
        text.title,
        text.content,
        text.language,
        USER_ID,
        text.section_id)

    return {"result": str(result)}

@router.get("/{text_id}")
async def get_text(text_id: str):
    try:
        result = await db_get_text(text_id)
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="Text not found")

@router.put("/{text_id}", status_code=200)
async def put_text(text_id, text: TextCreate = Body(...)):
    try:
        result = await db_update_text(
            text_id,
            text.title,
            text.language,
            text.section_id
        )
        return {"result": result}
    except ValueError:
        raise HTTPException(status_code=404, detail="Text not found")

@router.delete("/{text_id}", status_code=204)
async def delete_text(text_id: str):
    try:
        await db_delete_text(text_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Text not found")