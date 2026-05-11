import os
import httpx
from fastapi import APIRouter, Request

from ai.groq_client import chat, reset

router = APIRouter()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE = f"https://api.telegram.org/bot{TOKEN}"


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text})


@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message") or data.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user_id = f"telegram_{chat_id}"

    if text.strip().lower() in ("/start", "/reset"):
        reset(user_id)
        await send_message(chat_id, "Olá! Sou o teu assistente. Como posso ajudar?")
        return {"ok": True}

    if text:
        reply = await chat(user_id, text)
        await send_message(chat_id, reply)

    return {"ok": True}


async def set_webhook(base_url: str):
    webhook_url = f"{base_url}/webhook/telegram"
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE}/setWebhook", json={"url": webhook_url})
