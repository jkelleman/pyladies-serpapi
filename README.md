# PyLadies Skill Gap Analyzer 📊🔍

An automated data pipeline designed to analyze educational trends and identify "skill gaps" across local **PyLadies** chapters. By leveraging **SerpApi**, the tool maps out existing chapter locations, extracts technologies taught in past events, and compares them with current job market demands.

## 🚀 Features

- **Automated Chapter Discovery:** Uses Google Custom Search operators via SerpApi (`site:meetup.com`) to dynamically map out PyLadies chapters without getting blocked by anti-bot protections.
- **Instagram Profile Scraping:** Uses the SerpApi `instagram_profile` engine to safely extract biography and update descriptions from local chapters' public profiles.
- **Skill Taxonomy Matching:** Cross-references extracted textual data against a predefined Python ecosystem taxonomy (e.g., Django, FastAPI, Data Science, Pandas).
- **Visual Analytics:** Automatically generates comparative bar charts and exports data into clean Markdown reporting files.

---

## 📂 Project Structure

The project follows a clean, modular python architecture separated by business logic constraints:

```text
pyladies-serpapi/
├── src/
│   ├── __init__.py          # Package initializer
│   ├── config.py            # Static variables and skill taxonomies
│   ├── data_fetcher.py      # Network calls (SerpApi, Meetup, Instagram)
│   ├── analyzer.py          # Data processing and skill mapping logic
│   └── reporter.py          # Visual graph generation and Markdown reporting
├── main.py                  # CLI argument parser and pipeline orchestrator
├── requirements.txt         # Project dependencies
└── .env                     # Local environment credentials
```

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd pyladies-serpapi
   ```

2. **Set up a Python Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you are running on macOS with default LibreSSL bindings, `urllib3<2` is pre-configured to avoid initialization warnings.*

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your SerpApi credential token:
   ```env
   SERPAPI_KEY="your_secret_serpapi_api_key_here"
   ```

---

## 💻 Usage

Run the orchestrator script using the command-line interface. You must provide arguments using the correct hyphenation flags (`--`).

### Basic Analysis
Analyze events hosted within the last 6 months:
```bash
python main.py --history-months 6
```

### Investigate a Specific Instagram Chapter
Pull biography profile insights using SerpApi's specialized social engine:
```bash
python main.py --instagram-user pyladiesbr
```

### Full Dump Configuration
Discover and rebuild the local chapters index mapping database:
```bash
python main.py --dump-chapters
```

---

## 📈 Outputs
All generated execution reports, data tables, and Matplotlib data visualization png figures are saved directly into the dynamically created `outputs/` folder.
