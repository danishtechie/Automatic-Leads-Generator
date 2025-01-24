import requests
import logging
import threading
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from config import GOOGLE_API_URL, GOOGLE_API_KEY, GOOGLE_CX, CRUNCHBASE_API_KEY, CRUNCHBASE_API_URL


# Logger Setup
logging.basicConfig(filename='logs/scraper.log', level=logging.INFO)


# Email validation helper
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    excluded_patterns = [r'-relay-', r'@nivo-bar-', r'@webpack' , r'@o418887.ingest.sentry.io', r'@sentry.io', r'@2x.png', r'@2x-1.png', r'yourname@company.com', r'flags@2x-140042eba8c90ae1cede87fe8fcb27f0.png']
    if not re.match(email_pattern, email):
        return False
    for pattern in excluded_patterns:
        if re.search(pattern, email):
            return False
    return True



# Google API call
def get_data_from_google(query, search_type="company"):
    try:
        params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CX, 'q': query}
        response = requests.get(GOOGLE_API_URL, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            if 'items' in data:
                return data['items']
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Google API error for {query}: {e}")
        return []

# Crunchbase API call
def get_data_from_crunchbase(query, collection="organizations"):
    try:
        params = {
            'user_key': CRUNCHBASE_API_KEY,
            'query': query,
            'collection_ids': collection,
            'limit': 20
        }
        response = requests.get(CRUNCHBASE_API_URL, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'items' in data['data']:
                return data['data']['items']
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Crunchbase API error for {query}: {e}")
        return []



def extract_emails_from_webpage(url):
    """Fetches a webpage and extracts email addresses."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
    except requests.RequestException:
        return []



def fetch_metadata_from_page(url):
    """Fetches metadata (description, social links) from a page."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract meta description
        description = (
            soup.find("meta", attrs={"name": "description"}) or
            soup.find("meta", attrs={"property": "og:description"})
        )
        description = description["content"] if description else "No description found"

        # Extract the first valid social link
        social_link = None
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']

            # Define stricter patterns for user profiles
            if (
                    ("linkedin.com/in/" in href) or  # LinkedIn personal profile
                    ("linkedin.com/company/" in href) or  # LinkedIn company profile
                    ("facebook.com/" in href and "/user" in href) or  # Facebook user profile
                    ("facebook.com/" in href and "/pages/" in href) or  # Facebook pages
                    ("twitter.com/" in href and "status" not in href) or  # Avoid tweet links
                    ("instagram.com/" in href and not any(x in href for x in ["/explore/",
                                                                              "/reel/"])) or  # Instagram profiles (avoid reels/explore links)
                    ("youtube.com/channel/" in href) or  # YouTube channel link
                    ("youtube.com/user/" in href) or  # YouTube user link
                    ("github.com/" in href and not "/issues/" in href) or  # GitHub profile
                    ("medium.com/" in href and "/@" in href) or  # Medium profile
                    ("pinterest.com/" in href and "/pin/" not in href) or  # Pinterest profiles (avoid pins)
                    ("tiktok.com/@" in href)  # TikTok profile
            ):
                social_link = href
                break  # Stop after finding the first valid social link

        # Make the link clickable by using HTML anchor tags
        clickable_social_link = (
            f'<a href="{social_link}" target="_blank">{social_link}</a>' if social_link else "N/A"
        )

        return {
            "description": description,
            "social_links": clickable_social_link,
        }

    except Exception as e:
        logging.error(f"Error fetching metadata: {e}")
        return {
            "description": "Error fetching description",
            "social_links": "N/A"
        }


    except Exception as e:
        logging.error(f"Error fetching metadata: {e}")
        return {
            "description": "Error fetching description",
            "social_links": "N/A"
        }


def scrape_with_selenium(query):
    """Scrape Wikipedia search results using Selenium and enrich data."""
    options = Options()
    options.headless = True  # Run browser in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument("--disable-webgl")
    #user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    #options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=options)
    results = []

    try:
        # Navigate to Wikipedia search page
        #driver.get(f'https://en.wikipedia.org/w/index.php?search={query}')
        time.sleep(10)  # Wait for content to load

        # Confirm page title
        print(f"Page Title: {driver.title}")

        # Locate search results
        #results_elements = driver.find_elements(By.CSS_SELECTOR, '.mw-search-result-heading')
        #print(f"Found {len(results_elements)} results.")

        if not results_elements:
            print("No results found. Verify the CSS selector or page structure.")
            return []

        # Process each result
        for result in results_elements:
            try:
                title = result.find_element(By.TAG_NAME, 'a').text
                link = result.find_element(By.TAG_NAME, 'a').get_attribute('href')

                # Fetch metadata from the linked page
                metadata = fetch_metadata_from_page(link)

                # Attempt to extract emails from the linked page
                emails = extract_emails_from_webpage(link)
                email = emails[0] if emails else "N/A"

                # Add result to the list
                results.append({
                    "company": title,
                    "email": email,
                    "website_title": title,
                    "description": metadata["description"],
                    "link": link,
                    "social_links": metadata["social_links"],
                    "enriched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "Selenium"
                })

            except Exception as e:
                logging.error(f"Error processing result: {e}")
                continue

        return results

    except Exception as e:
        logging.error(f"Selenium error: {e}")
        return []

    finally:
        driver.quit()




def scrape_data_parallel(query):
    results = []
    threads = []

    # Google scraping function
    def scrape_from_google():
        data = get_data_from_google(query, search_type="Investors & Companies")
        if data:
            for item in data:
                snippet = item.get('snippet', 'No Description')
                link = item.get('link', '')
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', snippet)
                if not emails and link:
                    emails = extract_emails_from_webpage(link)
                email_display = ', '.join(emails[:1]) if emails else "N/A"

                metadata = fetch_metadata_from_page(link)

                # Validate email using is_valid_email
                if email_display != "N/A" and not is_valid_email(email_display):
                    continue  # Skip invalid emails

                results.append({
                    "company": item.get('title', 'Unknown'),
                    "email": email_display,
                    "website_title": item.get('title', 'No Title'),
                    "description": snippet or 'No Description',
                    "link": link if link else "Invalid or Unreachable URL",
                    "social_links": metadata["social_links"],
                    "enriched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "google"
                })

    # Crunchbase scraping function
    def scrape_from_crunchbase():
        data = get_data_from_crunchbase(query, collection="principal.investors")
        if data:
            for item in data:
                results.append({
                    "company": item.get('name', 'Unknown'),
                    "email": "N/A",  # No email from Crunchbase, add logic to extract if needed
                    "website_title": item.get('name', 'No Title'),
                    "description": item.get('short_description', 'No Description'),
                    "link": item.get('url', 'Invalid or Unreachable URL'),
                    "social_links": item.get('social_links', 'N/A'),  # If available, else 'N/A'
                    "enriched_at": format_timestamp(),  # Ensure the format is correct
                    "source": "Crunchbase"
                })

    # Third scraping function (for example, using Selenium)
    def scrape_from_selenium():
        data = scrape_with_selenium(query)
        if data[:5]:
            for item in data[:5]:
                results.append(item)

    # Start scraping in parallel threads
    threads.append(threading.Thread(target=scrape_from_google))
    threads.append(threading.Thread(target=scrape_from_crunchbase))
    threads.append(threading.Thread(target=scrape_from_selenium))  # Added third thread

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return results
# Timestamp helper
def format_timestamp():
    return datetime.now().strftime("%b %d, %Y, %I:%M %p")
