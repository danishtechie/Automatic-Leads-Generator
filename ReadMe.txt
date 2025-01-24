# Automatic Lead Generator

Automatic Lead Generator is a web application designed to scrape, enrich, and manage lead data. The project utilizes multiple scraping methods such as custom Google Search, Crunchbase API, and Selenium-based frontend automation to gather data. The application supports both manual and automatic scraping modes, leveraging threading for concurrent execution.

---

## Features

1. **Lead Scraping:**
   - Custom Google Search (requires API and URL).
   - Crunchbase API integration.
   - Frontend automation with Selenium.

2. **Data Enrichment:**
   - Scraped data is enriched with additional information for better insights.

3. **Database Integration:**
   - Uses SQLite3 to store and manage lead data.

4. **Visualization:**
   - Displays lead counts and other insights using Plotly graphs.

5. **Monitoring:**
   - Integrated with Prometheus for application performance monitoring.

6. **Threading:**
   - Enables concurrent scraping across multiple methods for efficiency.

---

## Requirements

- **chromedriver(front-end automation)
- **Python:** 3.8+
- **Libraries/Frameworks:**
  - Flask (Web application framework)
  - Selenium (Frontend automation)
  - Plotly (Data visualization)
  - Prometheus Client (Monitoring metrics)
  - SQLite3 (Database)

---

## Installation


. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

. Set up APIs and URLs:
   - **Google Custom Search API**
     - Obtain API Key and Search Engine ID from [Google Developers Console](https://console.developers.google.com/).
     - Add them to the `config.py` file.
   - **Crunchbase API**
     - Obtain API Key from [Crunchbase Developer Portal](https://developer.crunchbase.com/).
     - Add it to the `config.py` file.

. Run the application:
   ```bash
   python app.py
   ```

. Access the web app:
   - Open `http://127.0.0.1:5000/` in your browser.

---

## Configuration

- Create a `config.py` file with the following structure:
  ```python
  GOOGLE_API_KEY = "your_google_api_key"
  GOOGLE_CSE_ID = "your_google_cse_id"
  CRUNCHBASE_API_KEY = "your_crunchbase_api_key"
  ```

---

## Usage

1. **Manual Scraping:**
   - Navigate to the scraping page and input the query.
   - Select the desired method (Google, Crunchbase, Selenium).

2. **Automatic Scraping:**
   - Input the query and start scraping.
   - All methods will run concurrently using threads.

3. **View Leads:**
   - View scraped and enriched data in the database section.

4. **Visualization:**
   - Check the lead counts and insights on the dashboard with Plotly graphs.

---

## Technologies Used

- **Backend:** Flask
- **Frontend Automation:** Selenium
- **Visualization:** Plotly
- **Database:** SQLite3
- **Monitoring:** Prometheus

---

## Requirements File

Save the following content in a file named `requirements.txt`:
```plaintext
flask
selenium
plotly
prometheus_client
sqlite3
```

---

## Future Enhancements

- Support for additional APIs and scraping methods.
- Implementing a user authentication system.
- Adding more detailed dashboards and insights.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## Contact

For any queries, please contact [Danish Maqbool Baig](mailto:danishannu1111@gmail.com).

