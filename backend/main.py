from fastapi import FastAPI
from contextlib import asynccontextmanager

from services.database import client, vocabulary_collection
from routers.texts import router as text_router
from routers.sections import router as section_router
from routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await client.admin.command('ping')
        print('MongoDB connected')
        await vocabulary_collection.create_index(
            [("lemma", 1), ("lang", 1)],
            unique=True
        )
    except Exception as e :
        raise RuntimeError(f"MongoDB connection failed: {e}")

    yield

app = FastAPI(lifespan=lifespan)
app.include_router(text_router)
app.include_router(section_router)
app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}