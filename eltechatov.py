import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram import Bot
import feedparser

# Telegram Bot Token and Chat ID
TOKEN = '6621303717:AAFRM_YO5J2VHbL5DQHNuBRm5BrBilyn9Yk'
CHAT_ID = '-1002016795482'
bot = Bot(token=TOKEN)

# List of RSS Feed URLs
RSS_URLS = ["https://dotic.ir/rss/?cid=155", "https://dotic.ir/rss/?cid=144"]

# Track the most recent publication date for each feed
latest_pub_dates = {}

async def fetch_rss_with_selenium(url):
    # Configure Selenium to use Chrome in headless mode
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    # Navigate to the RSS URL
    driver.get(url)
    # Wait for redirection to complete and JavaScript to load
    await asyncio.sleep(30)
    # Get the source of the page, which should now be the RSS XML
    source = driver.page_source
    driver.quit()
    return source

async def fetch_rss_and_send_update():
    global latest_pub_dates
    while True:
        for url in RSS_URLS:
            # Fetch RSS using Selenium
            source = await fetch_rss_with_selenium(url)

            # Parse the RSS feed from the source obtained via Selenium
            feed = feedparser.parse(source)
            print(f"Processing feed: {url}")
            print(f"Number of entries: {len(feed.entries)}")
            if feed.entries:
                latest_entry = feed.entries[0]
                entry_pub_date = latest_entry.published_parsed

                # Use URL as a key to track publication date for each feed
                if url not in latest_pub_dates or entry_pub_date > latest_pub_dates.get(url, None):
                    latest_pub_dates[url] = entry_pub_date
                    message_text = f"📰 {latest_entry.title}\n{latest_entry.description}\nLink: {latest_entry.link}"
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=message_text)
                        print("New item sent from:", url)
                    except Exception as e:
                        print(f"Error sending message: {e}")

        await asyncio.sleep(300)  # Wait for 5 minutes before the next check

asyncio.run(fetch_rss_and_send_update())