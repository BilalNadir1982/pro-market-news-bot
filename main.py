import os
import json
import time
import requests
import feedparser
from telegram import Bot
from deep_translator import GoogleTranslator

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =========================
# MEMORY
# =========================
NEWS_FILE = "sent_news.json"

def load_news():
    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_news(data):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f)

sent_news = load_news()

# =========================
# SEND
# =========================
def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

# =========================
# RSS SOURCES (FULL MARKET)
# =========================
RSS_FEEDS = [

    # CRYPTO
    "https://cointelegraph.com/rss",
    "https://cryptoslate.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://bitcoinmagazine.com/.rss/full/",

    # FOREX / MACRO
    "https://www.fxstreet.com/rss/news",
    "https://www.forexlive.com/feed/",
    "https://www.dailyfx.com/feeds/market-news",

    # COMMODITIES
    "https://www.kitco.com/rss/news",
    "https://oilprice.com/rss/main",

    # TURKEY ECONOMY
    "https://www.dunya.com/rss",
    "https://www.bloomberght.com/rss",
    "https://www.paraanaliz.com/feed/",
    "https://www.ekonomim.com/rss"
]

# =========================
# KEYWORDS FILTER
# =========================
KEYWORDS = [
    "bitcoin","ethereum","crypto","binance","solana","xrp",
    "forex","usd","eur","fed","ecb","interest rate",
    "gold","oil","silver","brent",
    "tcmb","faiz","enflasyon","borsa","dolar",
    "etf","sec","whale","liquidation","hack","bullish","bearish"
]

# =========================
# TRANSLATION (AI LAYER)
# =========================
def translate_to_tr(text):

    try:
        tr = GoogleTranslator(source="auto", target="tr").translate(text)

        t = tr.lower()

        # FINANCE FIX LAYER
        fixes = {
            "yatırım tröstleri": "yatırım fonları",
            "köprü korkuları": "DeFi köprü güvenliği endişeleri",
            "rapor": "raporuna göre",
            "bildirildi": "bildirildiğine göre",
        }

        for k, v in fixes.items():
            t = t.replace(k, v)

        return t.capitalize()

    except:
        return "Çeviri alınamadı"

# =========================
# CATEGORY SYSTEM
# =========================
def category(title):

    t = title.lower()

    if any(x in t for x in ["bitcoin","ethereum","crypto","binance","xrp","solana"]):
        return "🪙 CRYPTO"

    if any(x in t for x in ["usd","eur","forex","fed","ecb"]):
        return "💱 FOREX"

    if any(x in t for x in ["gold","oil","silver","brent"]):
        return "🛢 COMMODITY"

    if any(x in t for x in ["tcmb","faiz","enflasyon","borsa","dolar"]):
        return "🇹🇷 TURKEY"

    return "🌍 GLOBAL"

# =========================
# DUPLICATE FILTER
# =========================
def is_duplicate(title):

    t = title.lower()

    for old in sent_news:

        o = old.lower()

        match = sum(1 for w in t.split() if w in o)

        if match >= 5:
            return True

    return False

# =========================
# NEWS ENGINE
# =========================
def get_news():

    count = 0

    for url in RSS_FEEDS:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:15]:

                title = entry.title.strip()
                link = entry.link

                low = title.lower()

                if not any(k in low for k in KEYWORDS):
                    continue

                if title in sent_news:
                    continue

                if is_duplicate(title):
                    continue

                sent_news.add(title)
                save_news(sent_news)

                tr = translate_to_tr(title)
                cat = category(title)

                msg = f"""
{cat}

🧠 AI ÖZET:
{tr}

🌍 ORİJİNAL:
{title}

🔗 {link}
"""

                send(msg)

                count += 1
                time.sleep(2)

                if count >= 8:
                    return

        except:
            continue

# =========================
# START
# =========================
send("🚀 PRO MARKET NEWS ENGINE V4 STARTED")

# =========================
# LOOP
# =========================
while True:

    try:

        get_news()

        time.sleep(900)

    except Exception as e:

        print(e)
        time.sleep(60)
