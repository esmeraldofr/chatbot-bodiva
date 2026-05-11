import os
from groq import Groq
from collections import defaultdict
from typing import List
from knowledge.bodiva_kb import BODIVA_KNOWLEDGE

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_base_prompt = os.getenv("BOT_SYSTEM_PROMPT", "És um assistente especializado da BODIVA — Bolsa de Dívida e Valores de Angola.")

SYSTEM_PROMPT = f"""{_base_prompt}

Tens acesso à seguinte base de conhecimento oficial da BODIVA. Usa-a para responder com precisão às perguntas dos utilizadores. Responde sempre no idioma do utilizador (português ou inglês). Quando não souberes a resposta com base neste conhecimento, diz honestamente que não tens essa informação e sugere que o utilizador contacte a BODIVA directamente em institucional@bodiva.ao ou (+244) 225 420 300.

{BODIVA_KNOWLEDGE}"""

MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 10  # mensagens por conversa

# histórico em memória: {platform_user_id: [messages]}
_history: dict[str, List[dict]] = defaultdict(list)


def chat(user_id: str, message: str) -> str:
    history = _history[user_id]
    history.append({"role": "user", "content": message})

    # manter histórico limitado
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


def reset(user_id: str) -> None:
    _history[user_id] = []
