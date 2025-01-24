import threading
import sqlite3
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import logging
from scraper import  scrape_data_parallel
from config import GOOGLE_API_URL, GOOGLE_CX, GOOGLE_API_KEY


DATABASE = "data/database.db"
# Logger Setup
logging.basicConfig(filename='logs/scheduler.log', level=logging.INFO)


def save_leads_to_db(leads):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for lead in leads:
        cursor.execute("""
            INSERT INTO leads (
                company, email, website_title, description, link, social_links, enriched_at, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead['company'], lead['email'], lead['website_title'], lead['description'], lead['link'],
            lead['social_links'], lead['enriched_at'], lead['source']
        ))

    conn.commit()
    conn.close()



class Scheduler:
    def __init__(self):
        self.running = True
        self.lock = threading.Lock()
        self.query_list = [
    # Indian News & Politics
    "current status of India's G20 initiatives 2025",
    "latest updates on Indian education reforms",
    "most discussed political scandals in India 2025",
    "impact of India's digital payments growth",
    "updates on Indian startup ecosystem policies",
    "India-China border news 2025",
    "top policy debates in Indian parliament 2025",
    "progress of India's smart cities mission",
    "Indian healthcare reforms in 2025",
    "latest news on India's defense exports",

    # Gaza News
    "current situation in Gaza and Israel 2025",
    "UN's role in mediating the Gaza conflict",
    "global humanitarian aid for Gaza 2025",
    "updates on Gaza ceasefire agreements",
    "economic challenges in Gaza post-conflict",
    "impact of Gaza conflict on Middle Eastern politics",
    "current status of Gaza reconstruction efforts",
    "Middle East peace talks latest developments",
    "regional reactions to the Gaza crisis",
    "human rights reports on Gaza 2025",

    # Global Technology Trends
    "AI-powered automation trends in 2025",
    "top advancements in quantum encryption",
    "current trends in AI-generated content tools",
    "growth of decentralized finance platforms",
    "emerging markets for AI chips in 2025",
    "top tech unicorns of 2025 globally",
    "latest developments in generative AI models",
    "advancements in AI healthcare diagnostics",
    "top global trends in 6G technology",
    "most downloaded AI apps of 2025",

    # Renewable Energy
    "breakthroughs in solar-to-hydrogen tech",
    "global advancements in wave energy solutions",
    "current news on fusion energy experiments",
    "most efficient EV batteries in 2025",
    "India's progress in solar energy capacity",
    "wind energy farms breaking efficiency records",
    "global green energy investments in 2025",
    "clean energy exports trends in 2025",
    "advancements in renewable biofuels",
    "future of urban green energy grids",

    # Space & Exploration
    "latest findings from James Webb Telescope",
    "current updates on Artemis missions to the Moon",
    "private companies racing to Mars in 2025",
    "India's Gaganyaan mission progress",
    "new satellite launches by SpaceX in 2025",
    "global collaboration on asteroid mining",
    "current plans for space tourism in 2025",
    "China's space exploration achievements 2025",
    "updates on new space stations under construction",
    "most promising space startups of 2025",

    # Science & Medicine
    "progress in mRNA technology for non-COVID vaccines",
    "AI-powered tools for mental health diagnostics",
    "breakthroughs in anti-aging treatments 2025",
    "gene therapy advancements for rare diseases",
    "latest news on organ bioprinting technologies",
    "top global trends in cancer research 2025",
    "AI's role in drug discovery acceleration",
    "advancements in wearable health devices",
    "global trends in antimicrobial resistance research",
    "innovations in personalized medicine 2025",

    # Business & Finance
    "top-performing fintech startups of 2025",
    "India's IPO boom: key companies to watch",
    "AI-driven investment tools dominating finance",
    "global trends in ESG (Environmental, Social, Governance) investing",
    "biggest mergers and acquisitions in Asia 2025",
    "impact of cryptocurrency regulation in 2025",
    "most influential global business leaders 2025",
    "current trends in cross-border e-commerce",
    "future of digital currencies backed by central banks",
    "most lucrative business sectors in 2025",

    # Entertainment & Media
    "top Netflix releases of 2025",
    "latest trends in OTT streaming platforms",
    "most anticipated video games of 2025",
    "highest-grossing movies worldwide 2025",
    "impact of AI on film production processes",
    "most popular influencers on YouTube in 2025",
    "global trends in music streaming platforms",
    "India's most-followed social media personalities",
    "rise of AI-generated art in 2025",
    "impact of virtual concerts on the music industry",

    # Miscellaneous Topics
    "advances in global urban sustainability 2025",
    "current trends in remote work technologies",
    "best destinations for eco-friendly travel 2025",
    "latest innovations in electric aviation",
    "future of autonomous delivery drones",
    "top breakthroughs in AI robotics for 2025",
    "global trends in 3D-printed housing",
    "emerging use cases for blockchain in logistics",
    "impact of climate change on agriculture 2025",
    "most advanced cities adopting IoT globally",
]




        self.current_query_index = 0

    def get_next_query(self):
        """
        Get the next query from the list in a round-robin fashion.
        """
        query = self.query_list[self.current_query_index]
        self.current_query_index = (self.current_query_index + 1) % len(self.query_list)
        return query

    def run_auto_google_scraping(self):
        while self.running:
            try:
                query = self.get_next_query()
                logging.info(f"Starting scraping for query: {query}")

                # Step 2: Scrape data using Selenium
                scraped_data = scrape_data_parallel(query)
                logging.info(f"Scraped data for query '{query}': {scraped_data}")

                # Step 3: Save scraped data to the database directly
                if scraped_data:
                    with self.lock:  # Ensure thread safety for DB operations
                        save_leads_to_db(scraped_data)
                        logging.info(f"Scraped data saved to the database for query: {query}")
                else:
                    logging.warning(f"No data scraped for query: {query}")

            except Exception as e:
                logging.error(f"Error in automated Google scraping: {str(e)}")

            time.sleep(30)

    def start(self):
        """
        Start the scheduled scraping and enrichment in a separate thread.
        """
        threading.Thread(target=self.run_auto_google_scraping, daemon=True).start()
        logging.info("Scheduler started for automated Google scraping and enrichment.")

    def stop(self):
        """
        Stop the scheduled scraping and enrichment gracefully.
        """
        self.running = False
        logging.info("Scheduler stopped gracefully.")