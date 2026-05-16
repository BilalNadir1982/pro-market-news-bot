import os
import requests
import feedparser
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

sent_news = set()

def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

# CRYPTO NEWS
def crypto_news():

    url = "https://cointelegraph.com/rss"

    feed = feedparser.parse(url)

    for entry in feed.entries[:5]:

        title = entry.title
        link = entry.link

        if title in sent_news:
            continue

        sent_news.add(title)

        msg = f"""
🚨 CRYPTO NEWS

📰 {title}

🔗 {link}
"""

        send(msg)

# FEAR & GREED
def fear_greed():

    url = "https://api.alternative.me/fng/"

    data = requests.get(url).json()

    value = data["data"][0]["value"]
    status = data["data"][0]["value_classification"]

    msg = f"""
📊 FEAR & GREED INDEX

Value: {value}

Mood: {status}
"""

    send(msg)

# BTC PRICE
def btc_price():

    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    data = requests.get(url).json()

    btc = data["bitcoin"]["usd"]

    send(f"₿ BTC PRICE: ${btc}")

if __name__ == "__main__":

    crypto_news()

    fear_greed()

    btc_price()
