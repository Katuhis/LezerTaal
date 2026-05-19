from bson import ObjectId
from fastapi import FastAPI, Body
from contextlib import asynccontextmanager

from models import TextCreate
from services.database import client
from services.texts import db_create_text, db_get_texts, db_get_text, db_update_text, db_delete_text


USER_ID='6a0c644e3ad7680112699251'


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        client.admin.command('ping')
        print('MongoDB connected')
    except Exception as e :
        raise RuntimeError(f"MongoDB connection failed: {e}")

    yield


app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/texts")
def get_texts():
    texts = db_get_texts(USER_ID)
    return {"result": texts}

@app.post("/texts", status_code=201)
def post_text(text: TextCreate = Body(...)):
    if text.title is None:
        text.title = ' '.join(text.content.split()[:5])

    result = db_create_text(
        text.title,
        text.content,
        text.language,
        USER_ID,
        text.section_id)

    return {"result": str(result)}

@app.get("/texts/{text_id}")
def get_text(text_id: str):
    return db_get_text(text_id)

@app.put("/texts/{text_id}")
def put_text(text_id, text: TextCreate = Body(...)):
    result = db_update_text(
        text_id,
        text.title,
        text.content,
        text.section_id
    )
    return {"updated": str(result)}

@app.delete("/texts/{text_id}", status_code=204)
def delete_text(text_id: str):
    db_delete_text(text_id)
