import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from platforms.telegram import router as telegram_router, set_webhook as set_telegram_webhook
from platforms.meta import router as meta_router
from platforms.tiktok import router as tiktok_router
from platforms.twitter import poll_mentions


BASE_URL = os.getenv("BASE_URL", "")  # ex: https://chatbot.onrender.com


@asynccontextmanager
async def lifespan(app: FastAPI):
    # configurar webhook do Telegram no arranque
    if BASE_URL and os.getenv("TELEGRAM_BOT_TOKEN"):
        await set_telegram_webhook(BASE_URL)

    # iniciar polling do Twitter em background
    if os.getenv("TWITTER_BEARER_TOKEN"):
        asyncio.create_task(poll_mentions(interval=60))

    yield


app = FastAPI(title="Social Media Chatbot", lifespan=lifespan)

app.include_router(telegram_router)
app.include_router(meta_router)
app.include_router(tiktok_router)


@app.get("/")
async def root():
    return {"status": "online", "platforms": ["telegram", "whatsapp", "instagram", "messenger", "tiktok", "twitter"]}
