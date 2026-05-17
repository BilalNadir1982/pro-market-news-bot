import os
import time
import json
import requests
import feedparser
from telegram import Bot

# =========================================
# TELEGRAM
# =========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =========================================
# MEMORY
# =========================================
NEWS_FILE = "sent_news.json"

def load_news():
    try:
        with open(NEWS_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_news(news_set):
    with open(NEWS_FILE, "w") as f:
        json.dump(list(news_set), f)

sent_news = load_news()

# =========================================
# SEND
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
    "https://cointelegraph.com/rss",
    "https://cryptoslate.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
]

# =========================================
# KEYWORDS
# =========================================
KEYWORDS = [
    "bitcoin",
    "ethereum",
    "etf",
    "fed",
    "sec",
    "binance",
    "blackrock",
    "solana",
    "xrp",
    "dogecoin",
    "whale",
    "hack",
    "lawsuit",
    "approval",
    "bullish",
    "bearish",
    "crash",
    "pump",
    "liquidation",
    "interest rate",
    "inflation"
]

# =========================================
# TURKISH SUMMARY
# =========================================
def translate_to_tr(text):

    t = text.lower()

    if "hack" in t:
        return "Kripto piyasasında siber saldırı endişesi oluştu."

    elif "etf" in t:
        return "ETF gelişmeleri piyasada büyük hareketlilik oluşturuyor."

    elif "fed" in t or "interest rate" in t:
        return "FED faiz politikaları piyasaları etkiliyor."

    elif "whale" in t:
        return "Balina hareketleri piyasada dikkat çekiyor."

    elif "bullish" in t:
        return "Piyasada yükseliş beklentisi güçleniyor."

    elif "bearish" in t:
        return "Piyasada düşüş baskısı artıyor."

    elif "liquidation" in t:
        return "Piyasada büyük likidasyon hareketi yaşanıyor."

    elif "bitcoin" in t:
        return "Bitcoin tarafında önemli gelişmeler yaşanıyor."

    return "Kripto piyasasında önemli bir gelişme yaşandı."

# =========================================
# DUPLICATE FILTER
# =========================================
def is_similar(title):

    title = title.lower()

    for old in sent_news:

        old = old.lower()

        same = 0

        for word in title.split():

            if word in old:
                same += 1

        if same >= 5:
            return True

    return False

# =========================================
# FEAR & GREED
# =========================================
def fear_greed():

    try:

        r = requests.get("https://api.alternative.me/fng/").json()

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

        return value

    except Exception as e:
        print(e)
        return 50

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

{"📈 BTC market güçlü" if dom > 60 else "🚀 Altcoin hareketleri güçlenebilir"}
"""

        send(msg)

    except Exception as e:
        print(e)

# =========================================
# AI MARKET BIAS
# =========================================
def ai_bias(fng):

    try:

        btc = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        ).json()["bitcoin"]

        change = btc["usd_24h_change"]

        if change > 3 and fng > 60:
            bias = "🟢 STRONG BULLISH"

        elif change < -3 and fng < 40:
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
# NEWS ENGINE
# =========================================
def get_news():

    count = 0

    for url in RSS_FEEDS:

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries[:15]:

                title = entry.title.strip()
                link = entry.link

                low = title.lower()

                # keyword filter
                if not any(k in low for k in KEYWORDS):
                    continue

                # duplicate
                if title in sent_news:
                    continue

                # similar duplicate
                if is_similar(title):
                    continue

                sent_news.add(title)
                save_news(sent_news)

                tr = translate_to_tr(title)

                msg = f"""
🚨 PRO MARKET NEWS

🇬🇧 EN:
{title}

🇹🇷 TR:
{tr}

🔗 {link}
"""

                send(msg)

                count += 1

                time.sleep(2)

                if count >= 5:
                    return

        except Exception as e:
            print(e)

# =========================================
# START
# =========================================
send("🚀 PRO AI MARKET SYSTEM STARTED")

# =========================================
# LOOP
# =========================================
while True:

    try:

        # FEAR & GREED
        fng = fear_greed()

        time.sleep(3)

        # BTC DOMINANCE
        btc_dominance()

        time.sleep(3)

        # AI BIAS
        ai_bias(fng)

        time.sleep(3)

        # NEWS
        get_news()

        # 15 dakika bekle
        time.sleep(900)

    except Exception as e:

        print(e)

        time.sleep(60)
