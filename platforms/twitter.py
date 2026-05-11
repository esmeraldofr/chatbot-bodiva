"""
Twitter/X — responde a menções (@bot) usando polling.
A API gratuita do X não suporta webhooks de DMs sem tier pago.
"""
import os
import asyncio
import httpx
from datetime import datetime, timezone

from ai.groq_client import chat

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

_last_id: str | None = None


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}


async def get_mentions(since_id: str | None = None) -> list[dict]:
    params = {"max_results": 10, "tweet.fields": "author_id,text"}
    if since_id:
        params["since_id"] = since_id

    async with httpx.AsyncClient() as client:
        # obtém o ID do bot primeiro
        me = await client.get("https://api.twitter.com/2/users/me", headers=_auth_headers())
        user_id = me.json().get("data", {}).get("id")
        if not user_id:
            return []

        r = await client.get(
            f"https://api.twitter.com/2/users/{user_id}/mentions",
            headers=_auth_headers(),
            params=params,
        )
        return r.json().get("data", [])


async def reply_tweet(tweet_id: str, author_id: str, text: str):
    # OAuth 1.0a necessário para publicar — simplificado com httpx-oauth ou tweepy
    # Por ora registamos a resposta (integrar tweepy para envio real)
    print(f"[Twitter] Resposta ao tweet {tweet_id}: {text[:80]}")


async def poll_mentions(interval: int = 60):
    global _last_id
    while True:
        try:
            mentions = await get_mentions(since_id=_last_id)
            for tweet in reversed(mentions):
                tweet_id = tweet["id"]
                author_id = tweet["author_id"]
                text = tweet["text"]
                user_id = f"twitter_{author_id}"
                reply = await chat(user_id, text)
                await reply_tweet(tweet_id, author_id, reply)
                _last_id = tweet_id
        except Exception as e:
            print(f"[Twitter] Erro: {e}")
        await asyncio.sleep(interval)
