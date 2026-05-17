import os
import json
import time
import requests
import feedparser
from telegram import Bot

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =========================
# NEWS MEMORY FILE
# =========================
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

# =========================
# SEND TELEGRAM
# =========================
def send(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    except Exception as e:
        print(e)

# =========================
# IMPORTANT FILTERS
# =========================
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
    "hack",
    "lawsuit",
    "approval",
    "bullish",
    "bearish",
    "crash",
    "pump",
    "whale",
    "liquidation",
    "interest rate",
    "inflation"
]

# =========================
# SIMPLE TURKISH SUMMARY
# =========================
def translate_to_tr(text):

    t = text.lower()

    if "lawsuit" in t:
        return "Şirket veya proje hakkında dava kaynaklı önemli gelişme yaşanıyor."

    elif "etf" in t:
        return "ETF ile ilgili gelişme piyasada hareketlilik oluşturuyor."

    elif "hack" in t:
        return "Kripto piyasasında güvenlik ve siber saldırı endişesi oluştu."

    elif "fed" in t or "interest rate" in t:
        return "FED faiz politikaları piyasayı etkileyebilecek durumda."

    elif "bullish" in t:
        return "Piyasada yükseliş beklentisi güçleniyor."

    elif "bearish" in t:
        return "Piyasada düşüş baskısı dikkat çekiyor."

    elif "bitcoin" in t:
        return "Bitcoin ile ilgili önemli bir piyasa gelişmesi yaşanıyor."

    elif "ethereum" in t:
        return "Ethereum tarafında önemli bir gelişme gündemde."

    elif "solana" in t:
        return "Solana ekosistemiyle ilgili dikkat çeken haber yayımlandı."

    elif "xrp" in t:
        return "XRP ile ilgili önemli bir gelişme yaşanıyor."

    elif "binance" in t:
        return "Binance ile ilgili piyasayı etkileyebilecek haber geldi."

    elif "whale" in t:
        return "Balina hareketleri piyasada dikkat çekiyor."

    elif "liquidation" in t:
        return "Piyasada yüksek miktarda likidasyon gerçekleşiyor."

    return "Kripto piyasasında önemli bir gelişme yaşandı."

# =========================
# RSS SOURCES
# =========================
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://cryptoslate.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
]

# =========================
# DUPLICATE CHECK
# =========================
def is_similar(title):

    title = title.lower()

    for old in sent_news:

        old = old.lower()

        # benzerlik kontrolü
        same_words = 0

        for word in title.split():

            if word in old:
                same_words += 1

        if same_words >= 5:
            return True

    return False

# =========================
# NEWS ENGINE
# =========================
def get_news():

    new_count = 0

    for feed_url in RSS_FEEDS:

        try:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:

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

                tr = translate_to_tr(title)

                msg = f"""
🚨 KRIPTO HABER

🇬🇧 EN:
{title}

🇹🇷 TR:
{tr}

🔗 {link}
"""

                send(msg)

                new_count += 1

                time.sleep(3)

                # spam koruması
                if new_count >= 5:
                    return

        except Exception as e:
            print(e)

# =========================
# START
# =========================
send("🚀 PRO NEWS BOT STARTED")

# =========================
# LOOP
# =========================
while True:

    try:

        get_news()

        # 15 dakika
        time.sleep(900)

    except Exception as e:

        print(e)

        time.sleep(60)
