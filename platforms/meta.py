"""
Webhook unificado para WhatsApp Business, Instagram e Facebook Messenger.
Todas as plataformas Meta usam o mesmo formato de webhook.
"""
import os
import httpx
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse

from ai.groq_client import chat

router = APIRouter()
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "token_secreto")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
WHATSAPP_TOKEN = os.getenv("META_WHATSAPP_TOKEN", os.getenv("META_ACCESS_TOKEN"))
WHATSAPP_PHONE_ID = os.getenv("META_WHATSAPP_PHONE_ID")


# ── Funções de envio ──────────────────────────────────────────────────────────

async def send_whatsapp(to: str, text: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
        )
        print(f"[WhatsApp] send to {to}: {r.status_code} {r.text}")


async def send_messenger(recipient_id: str, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://graph.facebook.com/v19.0/me/messages",
            params={"access_token": ACCESS_TOKEN},
            json={"recipient": {"id": recipient_id}, "message": {"text": text}},
        )


async def send_instagram(recipient_id: str, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://graph.facebook.com/v19.0/me/messages",
            params={"access_token": ACCESS_TOKEN},
            json={"recipient": {"id": recipient_id}, "message": {"text": text}},
        )


# ── Webhook ───────────────────────────────────────────────────────────────────

@router.get("/webhook/meta")
async def meta_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Token inválido")


@router.post("/webhook/meta")
async def meta_webhook(request: Request):
    data = await request.json()

    for entry in data.get("entry", []):
        # WhatsApp
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") == "text":
                    sender = msg["from"]
                    text = msg["text"]["body"]
                    user_id = f"whatsapp_{sender}"
                    reply = await chat(user_id, text)
                    await send_whatsapp(sender, reply)

        # Messenger / Instagram
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            text = message.get("text")
            platform = "instagram" if "instagram" in str(entry.get("id", "")) else "messenger"

            if sender_id and text:
                user_id = f"{platform}_{sender_id}"
                reply = await chat(user_id, text)
                if platform == "instagram":
                    await send_instagram(sender_id, reply)
                else:
                    await send_messenger(sender_id, reply)

    return {"status": "ok"}
