import requests
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup

DATABASE = "data/database.db"


# Function to fetch metadata from URL
def fetch_metadata(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title and meta description
        title = soup.title.string if soup.title else "No title found"
        meta_description = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_description.get("content", "No meta description found") if meta_description else "No meta description"
        headers = [h1.text.strip() for h1 in soup.find_all("h1")]

        return {"title": title, "meta_description": meta_description, "headers": headers}
    except requests.exceptions.RequestException:
        return {"title": "Error fetching metadata", "meta_description": None, "headers": []}


# Simplified function to enrich leads with metadata
def enrich_leads():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch leads with a valid link
    cursor.execute("SELECT id, link FROM leads WHERE link IS NOT NULL AND link != ''")
    leads = cursor.fetchall()

    # Prepare a list for batch updates
    updates = []

    # Enrich each lead with metadata from the URL
    for lead_id, url in leads:
        if not url.startswith("https"):
            url = f"https://{url}"  # Ensure the URL starts with http(s)

        metadata = fetch_metadata(url)  # Fetch metadata from the URL

        # Add the metadata update to the batch list
        updates.append((
            metadata["title"],
            metadata["meta_description"],
            datetime.now(),  # Current timestamp for enrichment
            lead_id
        ))

    # Batch update leads in the database
    cursor.executemany("""
        UPDATE leads
        SET website_title = ?, description = ?, enriched_at = ?, email = ?, company = ?, link = ?, social_links = ?, source = ?
        WHERE id = ?
    """, updates)

    conn.commit()
    conn.close()
    print(f"Enriched {len(updates)} leads successfully.")

