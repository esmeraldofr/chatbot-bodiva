"""
TikTok — responde a comentários em vídeos.
A API TikTok não permite bots de DMs; apenas comentários via TikTok Display API.
Requer aprovação de app no TikTok for Developers.
"""
import os
import httpx
from fastapi import APIRouter, Request

from ai.groq_client import chat

router = APIRouter()
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")


async def post_comment_reply(video_id: str, comment_id: str, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://open.tiktokapis.com/v2/comment/publish/",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={
                "video_id": video_id,
                "text": text,
                "reply_comment_id": comment_id,
            },
        )


@router.post("/webhook/tiktok")
async def tiktok_webhook(request: Request):
    data = await request.json()

    # TikTok envia eventos de comentários
    for event in data.get("events", []):
        if event.get("type") == "comment":
            comment = event.get("comment", {})
            video_id = comment.get("video_id")
            comment_id = comment.get("id")
            author_id = comment.get("author_id")
            text = comment.get("text", "")

            if text and video_id and comment_id:
                user_id = f"tiktok_{author_id}"
                reply = await chat(user_id, text)
                await post_comment_reply(video_id, comment_id, reply[:150])  # TikTok limita comentários

    return {"status": "ok"}
