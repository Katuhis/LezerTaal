from fastapi import FastAPI
from contextlib import asynccontextmanager

from services.database import client
from routers.texts import router as text_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        client.admin.command('ping')
        print('MongoDB connected')
    except Exception as e :
        raise RuntimeError(f"MongoDB connection failed: {e}")

    yield

app = FastAPI(lifespan=lifespan)
app.include_router(text_router)

@app.get("/health")
def health():
    return {"status": "ok"}