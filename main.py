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
    "blackrock", "sec"
]

def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

# ---------------- SIMPLE TRANSLATE ----------------
# (API YOK → basit Türkçe özet sistemi)

def translate_to_tr(text):

    text = text.lower()

    replacements = {
        "bitcoin": "Bitcoin",
        "ethereum": "Ethereum",
        "etf": "ETF",
        "inflation": "enflasyon",
        "rate": "faiz oranı",
        "crash": "sert düşüş",
        "pump": "yükseliş",
        "hack": "siber saldırı",
        "market": "piyasa",
        "approval": "onay",
        "sec": "ABD Menkul Kıymetler Kurulu"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.capitalize()

# ---------------- MARKET ----------------

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
        bias = "🟢 BULLISH"
    elif value < 30:
        bias = "🔴 BEARISH"
    else:
        bias = "🟡 SIDEWAYS"

    msg = f"""
📊 PRO V2 MARKET

₿ BTC: ${btc}
ETH: ${eth}

Dominance: {dominance:.2f}%

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
