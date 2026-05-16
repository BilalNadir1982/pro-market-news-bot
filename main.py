import os
import requests
import feedparser
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

sent = set()

IMPORTANT_KEYWORDS = [
    "etf", "fed", "inflation", "rate", "hack",
    "liquidation", "ban", "crash", "pump", "bitcoin"
]

def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

def is_important(title):
    t = title.lower()
    return any(k in t for k in IMPORTANT_KEYWORDS)

# ---------------- MARKET DATA ----------------

def market_data():

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

    value = fng["value"]
    mood = fng["value_classification"]

    # basit AI yorum
    if int(value) > 70:
        bias = "🟢 BULLISH MARKET"
    elif int(value) < 30:
        bias = "🔴 BEARISH MARKET"
    else:
        bias = "🟡 SIDEWAYS / UNCERTAIN"

    msg = f"""
📊 PRO MARKET UPDATE

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

        if not is_important(title):
            continue

        sent.add(title)

        msg = f"""
🚨 IMPORTANT CRYPTO NEWS

📰 {title}

🔗 {link}
"""

        send(msg)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    market_data()
    news()
