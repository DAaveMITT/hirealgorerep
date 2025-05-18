import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import os
import random
from datetime import datetime
from requests.exceptions import RequestException, ConnectionError, Timeout
from urllib.parse import urlparse

# ✅ Configure Logging
logging.basicConfig(
    filename="crypto_scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ✅ Directories
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ List of User-Agents (Rotates to Avoid Blocking)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36"
]

# ✅ List of User-Agents (Rotates to Avoid Blocking)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36"
]

# ✅ List of crypto news websites
CRYPTO_SITES = [
    "https://cryptoslate.com/",
    "https://www.coindesk.com/",
    "https://cointelegraph.com/",
    "https://decrypt.co/",
    "https://www.newsbtc.com/",
    "https://bitcoinist.com/",
    "https://ambcrypto.com/",
    "https://www.theblock.co/",
    "https://cryptonews.com/",
    "https://u.today/",
    "https://dailyhodl.com/",
    "https://cryptopotato.com/",
    "https://beincrypto.com/",
    "https://blockworks.co/news",
    "https://www.fxstreet.com/cryptocurrencies",
]

SITE_CONFIGS = {
    "cryptoslate.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "article.full-article p",
            "article.full-article div",
            "article.full-article span",
            "article.full-article blockquote",
            "article.full-article pre",
            "article.full-article code"
        ],
        "url_base": "https://cryptoslate.com",
    },

    "coindesk.com": {
        "headline_selector": "h3 a",
        "article_selectors": [
            "div.article__body p",
            "div.article__body div",
            "div.article__body span",
            "div.article__body blockquote",
            "div.article__body pre",
            "div.article__body code"
        ],
        "url_base": "https://www.coindesk.com",
    },

    "cointelegraph.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.post-content p",
            "div.post-content div",
            "div.post-content span",
            "div.post-content blockquote",
            "div.post-content pre",
            "div.post-content code"
        ],
        "url_base": "https://cointelegraph.com",
    },

    "decrypt.co": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.article-content p",
            "div.article-content div",
            "div.article-content span",
            "div.article-content blockquote",
            "div.article-content pre",
            "div.article-content code"
        ],
        "url_base": "https://decrypt.co",
    },

    "newsbtc.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.entry-content p",
            "div.entry-content div",
            "div.entry-content span",
            "div.entry-content blockquote",
            "div.entry-content pre",
            "div.entry-content code"
        ],
        "url_base": "https://www.newsbtc.com",
    },

    "bitcoinist.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.entry-content p",
            "div.entry-content div",
            "div.entry-content span",
            "div.entry-content blockquote",
            "div.entry-content pre",
            "div.entry-content code"
        ],
        "url_base": "https://bitcoinist.com",
    },

    "ambcrypto.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.content p",
            "div.content div",
            "div.content span",
            "div.content blockquote",
            "div.content pre",
            "div.content code"
        ],
        "url_base": "https://ambcrypto.com",
    },

    "theblock.co": {
        "headline_selector": "h3 a",
        "article_selectors": [
            "div.article-body p",
            "div.article-body div",
            "div.article-body span",
            "div.article-body blockquote",
            "div.article-body pre",
            "div.article-body code"
        ],
        "url_base": "https://www.theblock.co",
    },

    "cryptonews.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.article-content p",
            "div.article-content div",
            "div.article-content span",
            "div.article-content blockquote",
            "div.article-content pre",
            "div.article-content code"
        ],
        "url_base": "https://cryptonews.com",
    },

    "u.today": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.article p",
            "div.article div",
            "div.article span",
            "div.article blockquote",
            "div.article pre",
            "div.article code"
        ],
        "url_base": "https://u.today",
    },

    "dailyhodl.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.td-post-content p",
            "div.td-post-content div",
            "div.td-post-content span",
            "div.td-post-content blockquote",
            "div.td-post-content pre",
            "div.td-post-content code"
        ],
        "url_base": "https://dailyhodl.com",
    },

    "cryptopotato.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.entry-content p",
            "div.entry-content div",
            "div.entry-content span",
            "div.entry-content blockquote",
            "div.entry-content pre",
            "div.entry-content code"
        ],
        "url_base": "https://cryptopotato.com",
    },

    "beincrypto.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.article-content p",
            "div.article-content div",
            "div.article-content span",
            "div.article-content blockquote",
            "div.article-content pre",
            "div.article-content code"
        ],
        "url_base": "https://beincrypto.com",
    },

    "blockworks.co": {
        "headline_selector": "h3 a",
        "article_selectors": [
            "div.article-content p",
            "div.article-content div",
            "div.article-content span",
            "div.article-content blockquote",
            "div.article-content pre",
            "div.article-content code"
        ],
        "url_base": "https://blockworks.co/news",
    },

    "fxstreet.com": {
        "headline_selector": "h2 a",
        "article_selectors": [
            "div.entry-content p",
            "div.entry-content div",
            "div.entry-content span",
            "div.entry-content blockquote",
            "div.entry-content pre",
            "div.entry-content code"
        ],
        "url_base": "https://www.fxstreet.com/cryptocurrencies",
    },
}



# Temporarily block websites with too many failures
BLOCKED_SITES = {}

# Load previously scraped URLs
def load_scraped_urls():
    scraped_urls_file = os.path.join(DATA_DIR, "scraped_urls.json")
    if os.path.exists(scraped_urls_file):
        with open(scraped_urls_file, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# Save scraped URLs
def save_scraped_urls(urls):
    scraped_urls_file = os.path.join(DATA_DIR, "scraped_urls.json")
    if os.path.exists(scraped_urls_file):
        with open(scraped_urls_file, "r", encoding="utf-8") as f:
            existing_urls = set(json.load(f))
        urls = list(existing_urls.union(urls))
    with open(scraped_urls_file, "w", encoding="utf-8") as f:
        json.dump(list(urls), f, indent=4)

# Scrape a single article
def scrape_article(url, session, site_failures):
    """Scrapes a single article and saves it immediately to /data."""

    domain = urlparse(url).netloc.replace("www.", "")
    
    if domain in BLOCKED_SITES and time.time() - BLOCKED_SITES[domain] < 1800:
        logging.warning(f"⏳ Skipping blocked site: {url}")
        return None

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 403:
            logging.warning(f"⚠️ 403 Forbidden on {url}. Retrying with a different User-Agent...")
            time.sleep(random.randint(10, 30))
            headers["User-Agent"] = random.choice(USER_AGENTS)
            response = session.get(url, headers=headers, timeout=10)

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        headline = soup.title.string if soup.title else "No Title"
        article_content = []

        # Fetch paragraphs, spans, blockquotes, and other inline elements
        for selector in SITE_CONFIGS.get(domain, {}).get("article_selectors", ["p"]):
            elements = soup.select(selector)
            for element in elements:
                article_content.append(element.get_text().strip())

        if not article_content:
            logging.warning(f"⚠️ No content found for {headline}")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        article_data = {
            "headline": headline,
            "url": url,
            "source": domain,
            "content": " ".join(article_content)
        }

        article_filename = f"{DATA_DIR}/scraped_{timestamp}.json"
        with open(article_filename, "w", encoding="utf-8") as f:
            json.dump(article_data, f, indent=4)

        logging.info(f"✅ Article saved: {article_filename}")

        # ✅ Reset failure count if successful
        site_failures[domain] = 0
        return url

    except (RequestException, Timeout, ConnectionError) as e:
        logging.error(f"❌ Error fetching {url}: {e}")
        site_failures[domain] += 1

        if site_failures[domain] >= 5:
            logging.warning(f"🚫 Too many failures for {domain}, blocking for 30 minutes.")
            BLOCKED_SITES[domain] = time.time()

    return None


# Main function
def run_scraper():
    """Runs the scraper continuously, skipping blocked sites."""
    logging.info("📰 Starting scraper...")

    session = requests.Session()
    site_failures = {urlparse(site).netloc.replace("www.", ""): 0 for site in CRYPTO_SITES}

    while True:
        for site in CRYPTO_SITES:
            if urlparse(site).netloc.replace("www.", "") in BLOCKED_SITES:
                continue  # Skip temporarily blocked sites
            
            new_url = scrape_article(site, session, site_failures)

            if new_url:
                save_scraped_urls(load_scraped_urls().union({new_url}))

            # Delay
            sleep_time = random.randint(5, 20)
            logging.info(f"⏳ Waiting {sleep_time} seconds before next request...")
            time.sleep(sleep_time)

        # failures = restart
        if all(v >= 5 for v in site_failures.values()):
            wait_time = random.randint(300, 600)  # Wait 5-10 minutes
            logging.warning(f"🚨 Too many failures, restarting in {wait_time} seconds...")
            time.sleep(wait_time)

if __name__ == "__main__":
    run_scraper()