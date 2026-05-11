# Social Media Chatbot

Chatbot com IA (Groq/Llama 3.3) para todas as redes sociais.

## Plataformas suportadas

| Plataforma | Tipo | Notas |
|---|---|---|
| Telegram | DMs + grupos | Webhook automático |
| WhatsApp | DMs | Requer Meta Business verificado |
| Instagram | DMs | Requer conta Business |
| Facebook Messenger | DMs | Requer página FB |
| Twitter/X | Menções | Polling (API free limitada) |
| TikTok | Comentários | Sem DMs disponíveis |

## Setup rápido

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# edita .env com as tuas chaves
```

### 3. Obter chave Groq (grátis)
- Vai a https://console.groq.com
- Cria conta e gera API key
- Coloca em `GROQ_API_KEY`

### 4. Configurar Telegram (mais fácil para começar)
- Fala com @BotFather no Telegram
- `/newbot` → copia o token
- Coloca em `TELEGRAM_BOT_TOKEN`

### 5. Correr localmente
```bash
uvicorn main:app --reload
```

### 6. Expor para internet (para webhooks)
```bash
# usando ngrok
ngrok http 8000
# copia o URL https e coloca em BASE_URL no .env
```

## Deploy no Render.com (grátis)

1. Faz push para GitHub
2. Liga o repo no Render.com
3. Usa o ficheiro `render.yaml` — configuração automática
4. Adiciona as variáveis de ambiente no dashboard do Render

## Configurar Meta (WhatsApp, Instagram, Messenger)

1. Vai a https://developers.facebook.com
2. Cria uma app → adiciona produto "WhatsApp" / "Messenger"
3. Configura webhook URL: `https://teu-url/webhook/meta`
4. Verify token: o valor que definiste em `META_VERIFY_TOKEN`
5. Subscreve aos eventos: `messages`

## Variáveis de ambiente

Vê `.env.example` para lista completa.
