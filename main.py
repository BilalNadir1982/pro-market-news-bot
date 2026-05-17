import os
import json
import time
import requests
import feedparser
from telegram import Bot
from deep_translator import GoogleTranslator

# =========================================
# TELEGRAM
# =========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =========================================
# MEMORY FILE
# =========================================
NEWS_FILE = "sent_news.json"

def load_news():
    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_news(news_set):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(news_set), f)

sent_news = load_news()

# =========================================
# SEND TELEGRAM
# =========================================
def send(msg):

    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)

    except Exception as e:
        print(e)

# =========================================
# RSS SOURCES
# =========================================
RSS_FEEDS = [

    # ================= CRYPTO =================
    "https://cointelegraph.com/rss",
    "https://cryptoslate.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://u.today/rss",

    # ================= FOREX =================
    "https://www.fxstreet.com/rss/news",
    "https://www.forexlive.com/feed/",
    "https://www.dailyfx.com/feeds/market-news",

    # ================= COMMODITIES =================
    "https://www.kitco.com/rss/news",
    "https://oilprice.com/rss/main",

    # ================= TURKISH MARKET =================
    "https://www.dunya.com/rss",
    "https://www.bloomberght.com/rss",
    "https://www.paraanaliz.com/feed/",
    "https://www.ekonomim.com/rss"
]

# =========================================
# KEYWORDS
# =========================================
KEYWORDS = [

    # CRYPTO
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "solana",
    "xrp",
    "dogecoin",
    "binance",
    "etf",
    "sec",
    "whale",
    "liquidation",
    "bullish",
    "bearish",
    "crypto",

    # FOREX
    "usd",
    "eur",
    "dollar",
    "fed",
    "interest rate",
    "ecb",
    "forex",

    # COMMODITIES
    "gold",
    "silver",
    "oil",
    "brent",
    "natural gas",

    # TURKEY
    "tcmb",
    "faiz",
    "enflasyon",
    "borsa",
    "dolar",
    "altın"
]

# =========================================
# REAL TRANSLATION
# =========================================
from deep_translator import GoogleTranslator

def translate_to_tr(text):

    try:
        raw = GoogleTranslator(source="auto", target="tr").translate(text)

        t = raw.lower()

        # ================= FIX LAYER =================

        t = t.replace("köprü korkuları", "DeFi köprü güvenliği endişeleri")
        t = t.replace("yatırım tröstleri", "yatırım fonları")
        t = t.replace("rapor", "raporuna göre")
        t = t.replace("bitcoin taşır", "Bitcoin transfer ediyor")

        # daha doğal finans dili düzeltmeleri
        t = t.replace("kripto yatırım ortaklıkları", "kripto yatırım fonları")

        return t.capitalize()

    except Exception as e:
        print(e)
        return "Çeviri alınamadı"
# =========================================
# DUPLICATE FILTER
# =========================================
def is_similar(title):

    title = title.lower()

    for old in sent_news:

        old = old.lower()

        same_words = 0

        for word in title.split():

            if word in old:
                same_words += 1

        if same_words >= 5:
            return True

    return False

# =========================================
# FEAR & GREED
# =========================================
def fear_greed():

    try:

        r = requests.get(
            "https://api.alternative.me/fng/"
        ).json()

        value = int(r["data"][0]["value"])
        label = r["data"][0]["value_classification"]

        if value >= 70:
            emoji = "🟢"

        elif value <= 30:
            emoji = "🔴"

        else:
            emoji = "🟡"

        msg = f"""
📊 FEAR & GREED INDEX

{emoji} Score: {value}
📌 Status: {label}
"""

        send(msg)

    except Exception as e:
        print(e)

# =========================================
# BTC DOMINANCE
# =========================================
def btc_dominance():

    try:

        r = requests.get(
            "https://api.coingecko.com/api/v3/global"
        ).json()

        dom = r["data"]["market_cap_percentage"]["btc"]

        msg = f"""
👑 BTC DOMINANCE

₿ BTC Dominance: {round(dom,2)}%

{"📈 BTC market dominance güçlü" if dom > 60 else "🚀 Altcoin market güçleniyor"}
"""

        send(msg)

    except Exception as e:
        print(e)

# =========================================
# AI MARKET BIAS
# =========================================
def ai_bias():

    try:

        btc = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        ).json()["bitcoin"]

        change = btc["usd_24h_change"]

        if change > 3:
            bias = "🟢 STRONG BULLISH"

        elif change < -3:
            bias = "🔴 STRONG BEARISH"

        else:
            bias = "🟡 SIDEWAYS"

        msg = f"""
🧠 AI MARKET BIAS

📈 BTC 24H: {round(change,2)}%
⚡ Bias: {bias}
"""

        send(msg)

    except Exception as e:
        print(e)

# =========================================
# CATEGORY DETECT
# =========================================
def category(title):

    t = title.lower()

    if any(x in t for x in ["bitcoin", "ethereum", "crypto", "xrp", "solana", "binance"]):
        return "🪙 CRYPTO NEWS"

    elif any(x in t for x in ["usd", "eur", "fed", "ecb", "forex"]):
        return "💱 FOREX NEWS"

    elif any(x in t for x in ["gold", "silver", "oil", "brent", "gas"]):
        return "🛢 COMMODITY NEWS"

    elif any(x in t for x in ["tcmb", "faiz", "enflasyon", "borsa", "dolar"]):
        return "🇹🇷 TURKEY MARKET"

    return "🌍 GLOBAL MARKET"

# =========================================
# NEWS ENGINE
# =========================================
def get_news():

    sent_count = 0

    for url in RSS_FEEDS:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:

                title = entry.title.strip()
                link = entry.link

                low = title.lower()

                # keyword filter
                if not any(k in low for k in KEYWORDS):
                    continue

                # exact duplicate
                if title in sent_news:
                    continue

                # similar duplicate
                if is_similar(title):
                    continue

                # save memory
                sent_news.add(title)
                save_news(sent_news)

                # translate
                tr = translate_to_tr(title)

                # category
                cat = category(title)

                msg = f"""
{cat}

🇬🇧 EN:
{title}

🇹🇷 TR:
{tr}

🔗 {link}
"""

                send(msg)

                sent_count += 1

                time.sleep(3)

                # spam koruma
                if sent_count >= 8:
                    return

        except Exception as e:
            print(e)

# =========================================
# START MESSAGE
# =========================================
send("🚀 PRO GLOBAL MARKET BOT STARTED")

# =========================================
# MAIN LOOP
# =========================================
while True:

    try:

        # MARKET DATA
        fear_greed()

        time.sleep(3)

        btc_dominance()

        time.sleep(3)

        ai_bias()

        time.sleep(3)

        # NEWS
        get_news()

        # 15 dakika
        time.sleep(900)

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(60)
