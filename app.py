from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import plotly.express as px
from prometheus_client import generate_latest, Counter
import subprocess
from scraper import scrape_data_parallel
from datetime import datetime
from enrich import enrich_leads
#from scheduler_auto import Scheduler

app = Flask(__name__)
DATABASE = "data/database.db"

# Prometheus Metrics Setup
lead_counter = Counter('leads_scraped', 'Number of leads scraped')



# Function to get DB connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Ensure we return rows as dictionaries
    return conn


def save_leads_to_db(leads):
    if not leads:
        print("No leads to save.")
        return

    try:
        conn = sqlite3.connect(DATABASE)  # Ensure this function connects to your database correctly
        cursor = conn.cursor()

        for lead in leads:
            print(f"Saving lead: {lead}")
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
        print("Leads saved successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        conn.close()


@app.route('/')
def index():
    conn = get_db_connection()

    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort = request.args.get('sort', 'recent')
    search_query = request.args.get('search', '')

    # Base query
    order_by = 'DESC' if sort == 'recent' else 'ASC'
    leads_query = f"SELECT * FROM leads WHERE company LIKE ? OR email LIKE ? OR description LIKE ? OR source LIKE ? ORDER BY enriched_at {order_by}"
    search_term = f"%{search_query}%"
    leads = conn.execute(leads_query, (search_term, search_term, search_term, search_term)).fetchall()

    # Pagination
    total_leads = len(leads)
    leads_paged = leads[(page - 1) * per_page:page * per_page]

    # Visualization
    lead_sources = [lead['source'] for lead in leads]
    lead_counts = {source: lead_sources.count(source) for source in set(lead_sources)}
    fig = px.bar(x=list(lead_counts.keys()), y=list(lead_counts.values()),
                 labels={'x': 'Lead Source', 'y': 'Count'}, title="Leads by Source")
    graph_html = fig.to_html(full_html=False)

    conn.close()
    return render_template('index.html', leads=leads_paged, graph_html=graph_html, total_leads=total_leads,
                           current_page=page, total_pages=len(leads) // per_page + 1, sort=sort, search=search_query)

# Export leads data to CSV and Excel
@app.route('/export', methods=['GET'])
def export_data():
    try:
        conn = get_db_connection()
        leads = conn.execute('SELECT * FROM leads').fetchall()
        conn.close()

        # Convert leads to a list of dictionaries for pandas
        leads_list = [dict(lead) for lead in leads]
        df = pd.DataFrame(leads_list)

        # Export to CSV
        csv_path = "data/leads_data.csv"
        df.to_csv(csv_path, index=False)

        # Export to Excel
        excel_path = "data/leads_data.xlsx"
        df.to_excel(excel_path, index=False)

        return jsonify({"message": "Export successful", "csv": csv_path, "excel": excel_path})
    except Exception as e:
        return jsonify({"message": f"Error exporting data: {str(e)}"})


# Prometheus Metrics Endpoint
@app.route('/metrics')
def metrics():
    return generate_latest(lead_counter)

@app.route('/trigger-scraper')
def trigger_scraper():
    try:
        query = "top 10 billionares"  # Or any other query you'd like to scrape
        leads_data = scrape_data_parallel(query)

        # Save the scraped data to the database
        save_leads_to_db(leads_data)

        return jsonify({"message": "Scraper triggered successfully", "leads": leads_data})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"})

@app.route('/enrich-leads')
def enrich():
    try:
        enrich_leads()
        return jsonify({"message": "Leads enrichment triggered successfully"})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"})




if __name__ == '__main__':
    #scheduler = Scheduler()
    #scheduler.start()
    app.run(debug=True)