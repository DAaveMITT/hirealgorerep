import requests
from bs4 import BeautifulSoup
import logging
import time
import random
import json
import os
import schedule
from typing import List, Dict, Optional, Set
from requests.exceptions import RequestException, ConnectionError, Timeout
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='crypto_scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CRYPTO_SITES = [
    "https://cryptoslate.com/",
    "https://www.coingecko.com/",
    "https://www.coindesk.com/",
    "https://cointelegraph.com/",
    "https://www.newsbtc.com/",
    "https://bitcoinist.com/",
    "https://ambcrypto.com/",
    "https://www.theblock.co/",
    "https://cryptonews.com/",
]

# element specifics
SITE_CONFIGS = {
    "cryptoslate.com": {
        "headline_selector": "h2 a",
        "article_selectors": ["article.full-article p", "div.entry-content p", "div.content p", "p", "div.article-body p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://cryptoslate.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or meta[name="pubdate"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "coingecko.com": {
        "headline_selector": "h3 a",
        "article_selectors": ["div.content p", "div.news-content p", "p", "div p", "article p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://www.coingecko.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "coindesk.com": {
        "headline_selector": "h3 a",
        "article_selectors": ["div.article__body p", "p", "div.content p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://www.coindesk.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "cointelegraph.com": {
        "headline_selector": "h2 a",
        "article_selectors": ["div.post-content p", "p", "div.content p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://cointelegraph.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "newsbtc.com": {
        "headline_selector": "h2 a",
        "article_selectors": ["div.entry-content p", "p", "div.content p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://www.newsbtc.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "bitcoinist.com": {
        "headline_selector": "h2 a",
        "article_selectors": ["div.entry-content p", "p", "div.content p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://bitcoinist.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "ambcrypto.com": {
        "headline_selector": "h2 a",
        "article_selectors": ["div.content p", "p", "div.article p", "article.content p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://ambcrypto.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "theblock.co": {
        "headline_selector": "h3 a",
        "article_selectors": ["div.article-body p", "p", "div.content p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://www.theblock.co",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
    "cryptonews.com": {
        "headline_selector": "h2 a",
        "article_selectors": ["div.article-content p", "p", "div.content p", "article p", "div p", "h1", "h2"],  # Expanded fallbacks
        "url_base": "https://cryptonews.com",
        "metadata_selectors": {
            "title": "title",
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "pub_date": 'meta[property="article:published_time"] or time[datetime]',
            "author": 'meta[name="author"] or span.author or div.author'
        }
    },
}

def load_scraped_urls() -> Set[str]:
    """Load previously scraped URLs from a persistent file."""
    data_dir = os.path.abspath('../data')
    os.makedirs(data_dir, exist_ok=True)
    scraped_urls_file = os.path.join(data_dir, 'scraped_urls.json')
    try:
        with open(scraped_urls_file, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_scraped_urls(urls: Set[str]) -> None:
    data_dir = os.path.abspath('../data')
    os.makedirs(data_dir, exist_ok=True)
    scraped_urls_file = os.path.join(data_dir, 'scraped_urls.json')
    try:
        with open(scraped_urls_file, 'w', encoding='utf-8') as f:
            json.dump(list(urls), f, indent=4, ensure_ascii=False)
        logging.info(f"Saved scraped URLs to {scraped_urls_file}")
    except Exception as e:
        logging.error(f"Error saving scraped URLs to {scraped_urls_file}: {str(e)}")

def extract_metadata(soup: BeautifulSoup, metadata_selectors: Dict) -> Dict:
    metadata = {}
    for key, selector in metadata_selectors.items():
        if isinstance(selector, str):
            elements = soup.select(selector)
        else:  # Handle OR logic for multiple selectors
            elements = []
            for s in selector.split(" or "):
                if elements or not soup.select(s):
                    continue
                elements = soup.select(s)
        
        if elements:
            if key == "title":
                metadata[key] = elements[0].get_text().strip() if elements[0].name == "title" else elements[0].get('content', '').strip() if elements[0].name == "meta" else ""
            elif key in ["description", "keywords"]:
                metadata[key] = elements[0].get('content', '').strip() if elements and elements[0].name == "meta" else ""
            elif key == "pub_date":
                for elem in elements:
                    if elem.name == "meta" and "content" in elem.attrs:
                        date_str = elem.get('content', '').strip()
                        try:
                            metadata[key] = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                            break
                        except ValueError:
                            continue
                    elif elem.name == "time" and "datetime" in elem.attrs:
                        date_str = elem.get('datetime', '').strip()
                        try:
                            metadata[key] = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                            break
                        except ValueError:
                            continue
            elif key == "author":
                for elem in elements:
                    if elem.name == "meta" and "content" in elem.attrs:
                        metadata[key] = elem.get('content', '').strip()
                    elif elem.name in ["span", "div"] and elem.get_text().strip():
                        metadata[key] = elem.get_text().strip()
                    if metadata.get(key):
                        break
    return metadata

def scrape_crypto_articles(url: str, config: Dict, previously_scraped_urls: Set[str]) -> List[Dict]:
    articles = []
    try:
        logging.info(f"Starting to scrape articles from {url}")
        headers = {
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape headlines and URLs
        headline_elements = soup.select(config["headline_selector"])
        for element in headline_elements[:10]:  # Limit to 10 articles per site
            headline = element.get_text().strip()
            if not headline:
                logging.warning(f"Skipped empty headline from {url}")
                continue
            
            article_url = element.get('href', '')
            if not article_url.startswith('http'):
                article_url = f"{config['url_base']}{article_url}"
            
            # Skip if URL was previously scraped
            if article_url in previously_scraped_urls:
                logging.info(f"Skipped previously scraped article: {headline[:50]}... from {article_url}")
                continue
            
            # Scrape article content and metadata with detailed debugging
            article_data = {
                "headline": headline,
                "url": article_url,
                "source": url.split("//")[1].split("/")[0]
            }
            try:
                article_response = requests.get(article_url, headers=headers, timeout=20)  # Increased timeout for larger pages
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # Extract full content
                article_content = []
                paragraphs_found = 0
                used_selector = None
                
                # Try multiple selectors in order, logging which one worked
                for selector in config["article_selectors"]:
                    content_elements = article_soup.select(selector)
                    if content_elements:
                        used_selector = selector
                        for content in content_elements:  # Scrape all paragraphs for full content
                            text = content.get_text().strip()
                            if text and not text.isspace():
                                article_content.append(text)
                                paragraphs_found += 1
                        if article_content:
                            break
                
                # Extract SEO metadata
                metadata = extract_metadata(article_soup, config["metadata_selectors"])
                article_data.update(metadata)
                
                full_article = " ".join(article_content) if article_content else None
                if full_article:
                    article_data["content"] = full_article
                else:
                    # Include detailed metadata and raw elements when content isn’t found
                    article_data["content"] = "No article content found."
                    article_data["debug_info"] = {
                        "paragraphs_found": paragraphs_found,
                        "http_status": article_response.status_code,
                        "content_length": len(article_soup.text.strip()) if article_soup.text else 0,
                        "selectors_tried": config["article_selectors"],
                        "used_selector": used_selector,
                        "response_headers": dict(article_response.headers),
                        "raw_elements": {
                            "h1": [elem.get_text().strip() for elem in article_soup.select("h1") if elem.get_text().strip()],
                            "h2": [elem.get_text().strip() for elem in article_soup.select("h2") if elem.get_text().strip()],
                            "div": [elem.get_text().strip() for elem in article_soup.select("div") if elem.get_text().strip() and len(elem.get_text().strip()) > 50],  # Limit to meaningful divs
                            "p": [elem.get_text().strip() for elem in article_soup.select("p") if elem.get_text().strip()]
                        }
                    }
                logging.info(f"Fetched new headline: {headline[:50]}... from {article_url} (used selector: {used_selector}, paragraphs found: {paragraphs_found})")
                
                articles.append(article_data)
            except (RequestException, Exception) as e:
                logging.error(f"Error fetching article content from {article_url}: {e}")
                article_data["content"] = "Failed to fetch article content."
                article_data["debug_info"] = {
                    "error": str(e),
                    "http_status": getattr(getattr(e.response, 'status_code', None), 'status_code', 'N/A') if hasattr(e, 'response') else 'N/A',
                    "response_headers": dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                    "raw_elements": {
                        "h1": [],
                        "h2": [],
                        "div": [],
                        "p": []
                    }
                }
                articles.append(article_data)
        
        if not articles:
            logging.warning(f"No new articles scraped from {url}")
        return articles[:5]  # Return top 5 new articles per site
    except (RequestException, Exception) as e:
        logging.error(f"Error scraping articles from {url}: {e}")
        return []

def job():
    """Job function to run the scraping task, ensuring only new articles are scraped."""
    try:
        logging.info("Starting crypto news scraping job...")
        previously_scraped_urls = load_scraped_urls()
        main(previously_scraped_urls)
        # Update the list of scraped URLs with new ones
        new_urls = {article["url"] for article in main(load_scraped_urls()) if "url" in article}
        all_scraped_urls = previously_scraped_urls.union(new_urls)
        save_scraped_urls(all_scraped_urls)
        logging.info("Crypto news scraping job completed successfully.")
    except Exception as e:
        logging.error(f"Error in scraping job: {e}")
        print(f"Error in scraping job: {e}")

def main(previously_scraped_urls: Set[str] = None):
    """Main function to scrape articles from all crypto news sites for review and SEO, filtering out previously scraped articles."""
    if previously_scraped_urls is None:
        previously_scraped_urls = set()
    
    all_articles = []
    for site in CRYPTO_SITES:
        domain = site.split("//")[1].split("/")[0]
        if domain in SITE_CONFIGS:
            articles = scrape_crypto_articles(site, SITE_CONFIGS[domain], previously_scraped_urls)
            all_articles.extend(articles)
            time.sleep(5)  # Increased delay between sites to avoid rate limits
        else:
            logging.warning(f"No configuration found for {site}")
    
    # Print or save results
    if all_articles:
        for article in all_articles:
            print(f"Headline: {article['headline']}")
            print(f"URL: {article['url']}")
            print(f"Content: {article['content'][:500] + '...' if len(article['content']) > 500 else article['content']}")
            print(f"Source: {article['source']}")
            if "title" in article:
                print(f"SEO Title: {article['title']}")
            if "description" in article:
                print(f"SEO Description: {article['description']}")
            if "keywords" in article:
                print(f"SEO Keywords: {article['keywords']}")
            if "pub_date" in article:
                print(f"Publication Date: {article['pub_date']}")
            if "author" in article:
                print(f"Author: {article['author']}")
            if "debug_info" in article and article["content"] == "No article content found.":
                print(f"Debug Info: {article['debug_info']}\n")
            else:
                print("\n")
        
        # Debug: Print all_articles before saving to ensure data exists
        logging.info(f"Number of new articles to save: {len(all_articles)}")
        logging.info(f"Sample new article: {all_articles[0] if all_articles else 'No new articles'}")
        
        # Save to JSON file with enhanced error handling and readable timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        data_dir = os.path.abspath('../data')
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, f'crypto_articles_{timestamp}.json')
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, indent=4, ensure_ascii=False)
            logging.info(f"Saved new articles to {filename}")
        except PermissionError as pe:
            logging.error(f"Permission denied saving to {filename}: {str(pe)}")
            print(f"Error: Permission denied saving to {filename}. Check directory permissions.")
        except IOError as ioe:
            logging.error(f"IO error saving to {filename}: {str(ioe)}")
            print(f"Error: IO error saving to {filename}. Check file system or disk space.")
        except Exception as e:
            logging.error(f"Unexpected error saving to {filename}: {str(e)}")
            print(f"Error: Unexpected error saving to {filename}. Check logs for details.")
    else:
        logging.warning("No new articles scraped from any site")
        print("Warning: No new articles were scraped from any site. Check logs for details.")
    
    return all_articles

def load_scraped_urls() -> Set[str]:
    """Load previously scraped URLs from a persistent file."""
    data_dir = os.path.abspath('../data')
    os.makedirs(data_dir, exist_ok=True)
    scraped_urls_file = os.path.join(data_dir, 'scraped_urls.json')
    try:
        with open(scraped_urls_file, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_scraped_urls(urls: Set[str]) -> None:
    """Save previously scraped URLs to a persistent file."""
    data_dir = os.path.abspath('../data')
    os.makedirs(data_dir, exist_ok=True)
    scraped_urls_file = os.path.join(data_dir, 'scraped_urls.json')
    try:
        with open(scraped_urls_file, 'w', encoding='utf-8') as f:
            json.dump(list(urls), f, indent=4, ensure_ascii=False)
        logging.info(f"Saved scraped URLs to {scraped_urls_file}")
    except Exception as e:
        logging.error(f"Error saving scraped URLs to {scraped_urls_file}: {str(e)}")

if __name__ == "__main__":
    # Schedule the job to run every 10 minutes
    schedule.every(10).minutes.do(job)
    
    # Run immediately once, then keep checking the schedule
    job()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for new jobs
        except KeyboardInterrupt:
            logging.info("Script terminated by user")
            print("Script terminated by user")
            break
        except Exception as e:
            logging.error(f"Error in scheduling loop: {e}")
            print(f"Error in scheduling loop: {e}")
            time.sleep(60)  # Wait before retrying