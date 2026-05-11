import os
import asyncio
from groq import Groq
from collections import defaultdict
from typing import List
from knowledge.bodiva_kb import BODIVA_KNOWLEDGE
from knowledge.live_data import is_market_query, fetch_live_market_data

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_base_prompt = os.getenv("BOT_SYSTEM_PROMPT", "És um assistente especializado da BODIVA — Bolsa de Dívida e Valores de Angola.")

SYSTEM_PROMPT = f"""És o assistente oficial da BODIVA — Bolsa de Dívida e Valores de Angola (www.bodiva.ao).

REGRAS ESTRITAS:
1. Responde APENAS com base na informação contida na base de conhecimento abaixo, retirada do site oficial www.bodiva.ao.
2. Se a pergunta não tiver resposta na base de conhecimento, diz: "Não tenho essa informação disponível. Para mais detalhes, contacte a BODIVA em institucional@bodiva.ao ou (+244) 225 420 300."
3. Não uses conhecimento geral, não especules, não inventes informação.
4. Não respondes a perguntas fora do âmbito da BODIVA (política, entretenimento, outros assuntos).
5. Responde sempre no idioma do utilizador (português ou inglês).

BASE DE CONHECIMENTO OFICIAL (fonte: www.bodiva.ao):
{BODIVA_KNOWLEDGE}"""

MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 10

_history: "Dict[str, List[dict]]" = defaultdict(list)


async def chat_async(user_id: str, message: str) -> str:
    # Perguntas de mercado/cotações — responder directamente com dados ao vivo
    if is_market_query(message):
        return await fetch_live_market_data()

    history = _history[user_id]
    history.append({"role": "user", "content": message})

    if len(history) > MAX_HISTORY * 2:
        history = history[-(MAX_HISTORY * 2):]
        _history[user_id] = history

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=1024,
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply


chat = chat_async


def reset(user_id: str) -> None:
    _history[user_id] = []
