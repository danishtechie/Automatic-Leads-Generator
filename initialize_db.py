import sqlite3
import os
import time

DATABASE_PATH = "data/database.db"

# Retry logic to handle database lock
def get_db_connection():
    attempt = 0
    while attempt < 5:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            return conn
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                attempt += 1
                time.sleep(1)  # Wait before retrying
            else:
                raise e
    raise Exception("Database is locked after multiple attempts")


def initialize_database():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = get_db_connection()  # Use the retry logic here
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    email TEXT,
    website_title TEXT,
    description TEXT,
    link TEXT,
    social_links TEXT,
    phone TEXT,
    location TEXT,
    keywords TEXT,
    enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contact_info TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON leads (email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON leads (company);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_show (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def add_contact_info_column():
    conn = get_db_connection()  # Use the retry logic here
    cursor = conn.cursor()

    # Add 'contact_info' column if not already present
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN contact_info TEXT;")
        conn.commit()
        print("contact_info column added successfully!")
    except sqlite3.OperationalError:
        print("Column 'contact_info' already exists.")

    conn.close()


def add_source_column():
    conn = get_db_connection()  # Use the retry logic here
    cursor = conn.cursor()

    # Add 'source' column if not already present
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN source TEXT;")
        conn.commit()
        print("source column added successfully!")
    except sqlite3.OperationalError:
        print("Column 'source' already exists or there is an issue.")

    conn.close()


def enable_wal_mode():
    conn = get_db_connection()  # Use the retry logic here
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    conn.commit()
    conn.close()
    print("WAL mode enabled for better concurrency.")

if __name__ == "__main__":
    initialize_database()
    enable_wal_mode()
    add_contact_info_column()
    add_source_column()
