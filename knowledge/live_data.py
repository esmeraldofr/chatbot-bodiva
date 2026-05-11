import httpx
from datetime import datetime

QUOTATIONS_URL = "https://www.bodiva.ao/capizar/last-quotation/api/v1/getLastQuotation_no.php"

MARKET_KEYWORDS = [
    "boletim", "cotaç", "cotac", "mercado", "preço", "preco", "titulo", "título",
    "obrigaç", "bilhete", "tesouro", "acç", "acao", "ação", "mbtt", "mbop", "mba",
    "mbup", "negoci", "bolsa", "resumo", "fecho", "encerr", "sesssão", "sessao",
    "today", "hoje", "diário", "diario", "bulletin", "quote", "stock", "price",
    "performance", "rendimento", "juro", "taxa"
]


def is_market_query(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in MARKET_KEYWORDS)


async def fetch_live_market_data() -> str:
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            r = await client.get(QUOTATIONS_URL)
            data = r.json()
    except Exception as e:
        return f"(Não foi possível obter dados ao vivo: {e})"

    if not data:
        return "(Sem dados de mercado disponíveis neste momento.)"

    today = datetime.now().strftime("%d/%m/%Y")
    lines = [f"📊 **Cotações BODIVA — {today}**\n"]

    by_type: dict = {}
    for item in data:
        t = item.get("typology", "Outro")
        by_type.setdefault(t, []).append(item)

    type_labels = {
        "OT-NR": "Obrigações do Tesouro Não Indexadas (OT-NR)",
        "OT-I": "Obrigações do Tesouro Indexadas (OT-I)",
        "BT": "Bilhetes do Tesouro (BT)",
        "Instrumento de Dívida": "Instrumentos de Dívida Privada",
        "Unidade de Participação": "Fundos de Investimento (UP)",
        "Acção": "Acções",
    }

    for typology, items in by_type.items():
        label = type_labels.get(typology, typology)
        lines.append(f"\n{label}:")
        for item in items:
            symbol = item.get("symbol", "—")
            price = item.get("price")
            coupon = item.get("couponRate")
            price_str = f"{price:.2f} AOA" if price is not None else "—"
            coupon_str = f" ({coupon}%)" if coupon else ""
            lines.append(f"  {symbol}: {price_str}{coupon_str}")

    lines.append(f"\n_Fonte: BODIVA — www.bodiva.ao_")
    return "\n".join(lines)
