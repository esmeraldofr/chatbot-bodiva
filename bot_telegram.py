"""
Modo polling — corre localmente sem precisar de servidor público.
Usa este ficheiro para testar o bot no Telegram.
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

from ai.groq_client import chat, reset

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE = f"https://api.telegram.org/bot{TOKEN}"


async def send(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text})


async def poll():
    offset = 0
    print(f"Bot online! Abre o Telegram e fala com o bot.")
    print("Pressiona Ctrl+C para parar.\n")

    async with httpx.AsyncClient(timeout=35) as client:
        while True:
            try:
                r = await client.get(
                    f"{BASE}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                )
                updates = r.json().get("result", [])

                for update in updates:
                    offset = update["update_id"] + 1
                    message = update.get("message") or update.get("edited_message")
                    if not message:
                        continue

                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    username = message.get("from", {}).get("first_name", "?")
                    user_id = f"telegram_{chat_id}"

                    print(f"[{username}]: {text}")

                    if text.strip().lower() in ("/start", "/reset"):
                        reset(user_id)
                        reply = "Olá! Sou o teu assistente com IA. Como posso ajudar?"
                    elif text:
                        reply = chat(user_id, text)
                    else:
                        continue

                    print(f"[Bot]: {reply}\n")
                    await send(chat_id, reply)

            except Exception as e:
                print(f"Erro: {e}")
                await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(poll())
