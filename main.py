import os
import requests
import feedparser
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

sent = set()

KEYWORDS = [
    "etf", "fed", "inflation", "rate", "hack",
    "liquidation", "crash", "pump", "bitcoin",
    "blackrock", "sec", "lawsuit"
]

def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

# ---------------- TURKISH SUMMARY ----------------

def translate_to_tr(text):

    t = text.lower()

    if "lawsuit" in t or "lawsuits" in t:
        return "Şirket hakkında açılan davalar, geleceği konusunda belirsizlik oluşturuyor."

    if "etf" in t and "bitcoin" in t:
        return "Bitcoin ETF gelişmeleri piyasada belirsizlik ve hareketlilik yaratıyor."

    if "fed" in t or "interest rate" in t or "rate" in t:
        return "FED faiz kararları kripto ve finans piyasalarını etkiliyor."

    if "hack" in t:
        return "Kripto piyasasında siber saldırı endişesi oluştu."

    if "crash" in t:
        return "Piyasada sert düşüş ve panik satış riski oluştu."

    if "pump" in t:
        return "Piyasada güçlü yükseliş hareketi görülüyor."

    if "bitcoin" in t:
        return "Bitcoin ile ilgili önemli piyasa gelişmesi yaşanıyor."

    return "Kripto piyasasında önemli bir gelişme yaşandı."

# ---------------- MARKET DATA ----------------

def market():

    btc = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    ).json()["bitcoin"]["usd"]

    eth = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    ).json()["ethereum"]["usd"]

    global_data = requests.get(
        "https://api.coingecko.com/api/v3/global"
    ).json()["data"]

    dominance = global_data["market_cap_percentage"]["btc"]

    fng = requests.get(
        "https://api.alternative.me/fng/"
    ).json()["data"][0]

    value = int(fng["value"])
    mood = fng["value_classification"]

    if value > 70:
        bias = "🟢 BULLISH MARKET"
    elif value < 30:
        bias = "🔴 BEARISH MARKET"
    else:
        bias = "🟡 SIDEWAYS MARKET"

    msg = f"""
📊 PRO V2 MARKET UPDATE

₿ BTC: ${btc}
ETH: ${eth}

BTC Dominance: {dominance:.2f}%

Fear & Greed: {value} ({mood})

⚡ Bias: {bias}
"""

    send(msg)

# ---------------- NEWS ----------------

def news():

    feed = feedparser.parse("https://cointelegraph.com/rss")

    for entry in feed.entries[:10]:

        title = entry.title
        link = entry.link

        if title in sent:
            continue

        if not any(k in title.lower() for k in KEYWORDS):
            continue

        sent.add(title)

        tr = translate_to_tr(title)

        msg = f"""
🚨 CRYPTO NEWS

🇬🇧 EN:
{title}

🇹🇷 TR:
{tr}

🔗 {link}
"""

        send(msg)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    market()
    news()
