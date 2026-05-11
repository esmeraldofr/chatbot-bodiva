import os
import asyncio
from groq import Groq
from collections import defaultdict
from typing import List
from knowledge.bodiva_kb import BODIVA_KNOWLEDGE
from knowledge.live_data import is_market_query, fetch_live_market_data

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_base_prompt = os.getenv("BOT_SYSTEM_PROMPT", "És um assistente especializado da BODIVA — Bolsa de Dívida e Valores de Angola.")

SYSTEM_PROMPT = f"""{_base_prompt}

Tens acesso à seguinte base de conhecimento oficial da BODIVA. Usa-a para responder com precisão às perguntas dos utilizadores. Responde sempre no idioma do utilizador (português ou inglês). Quando não souberes a resposta com base neste conhecimento, diz honestamente que não tens essa informação e sugere que o utilizador contacte a BODIVA directamente em institucional@bodiva.ao ou (+244) 225 420 300.

Quando recebes dados ao vivo do mercado (cotações), apresenta-os de forma clara e organizada. Não digas que não tens acesso a dados em tempo real — quando recebes esses dados, usa-os directamente.

{BODIVA_KNOWLEDGE}"""

MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 10

_history: "Dict[str, List[dict]]" = defaultdict(list)


async def chat_async(user_id: str, message: str) -> str:
    history = _history[user_id]

    # Injectar dados ao vivo se for pergunta sobre mercado
    user_content = message
    if is_market_query(message):
        live_data = await fetch_live_market_data()
        user_content = f"{message}\n\n[DADOS AO VIVO DO MERCADO BODIVA]\n{live_data}"

    history.append({"role": "user", "content": user_content})

    if len(history) > MAX_HISTORY * 2:
        history = history[-(MAX_HISTORY * 2):]
        _history[user_id] = history

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=1024,
    )

    reply = response.choices[0].message.content
    # Guardar no histórico a mensagem original (sem dados ao vivo)
    history[-1] = {"role": "user", "content": message}
    history.append({"role": "assistant", "content": reply})
    return reply


chat = chat_async


def reset(user_id: str) -> None:
    _history[user_id] = []
