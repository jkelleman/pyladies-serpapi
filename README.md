# PyLadies Skill Gap Analyzer

An automated data pipeline for analyzing educational trends and identifying skill gaps across local **PyLadies** chapters. The pipeline maps chapter locations, extracts technologies taught at past events, and benchmarks them against current developer market demand.

Built on **[SerpApi](https://serpapi.com)** to bypass anti-bot restrictions and access structured social profile data without brittle HTML scraping.

---

## Powered by SerpApi

Rather than maintaining fragile scrapers that break on Cloudflare challenges or DOM changes, this project routes all data extraction through SerpApi's purpose-built engines:

1. **Google Search API (`site:` operator):** Discovers PyLadies chapters indexed on Meetup without triggering bot-detection layers. See the [SerpApi Google Search API Documentation](https://serpapi.com).
2. **Instagram Profile API (`engine: instagram_profile`):** Pulls biography text and profile metadata from public chapter accounts. See the [SerpApi Instagram Profile API Documentation](https://serpapi.com).

Structured search results are more reliable, more maintainable, and significantly less brittle than scraping raw HTML.

---

## Features

- **Automated Chapter Discovery:** Uses Google's indexed database via SerpApi to enumerate valid chapter URLs at scale.
- **Social Profile Extraction:** Pulls public Instagram account data for local chapters using SerpApi's social engine.
- **Skill Taxonomy Matching:** Cross-references extracted text against a predefined Python ecosystem taxonomy covering frameworks, tools, and domains (e.g., Django, FastAPI, Data Science, Pandas).
- **Visual Analytics:** Generates comparative bar charts and exports structured Markdown reports for each pipeline run.

---

## Project Structure

```text
pyladies-serpapi/
├── src/
│   ├── __init__.py          # Package initializer
│   ├── config.py            # Static variables and skill taxonomies
│   ├── data_fetcher.py      # Network calls using SerpApi engines
│   ├── analyzer.py          # Data processing and skill mapping logic
│   └── reporter.py          # Visual graph generation and Markdown reporting
├── main.py                  # CLI argument parser and pipeline orchestrator
├── requirements.txt         # Project dependencies
└── .env                     # Local environment credentials
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd pyladies-serpapi
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or with `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```
   See the [SerpApi Python SDK Repository](https://github.com) for additional setup details.

4. **Configure environment variables:**
   Create a `.env` file at the project root and add your SerpApi key:
   ```env
   SERPAPI_KEY="your_secret_serpapi_api_key_here"
   ```

---

## Usage

The pipeline is driven through a CLI with `--`-prefixed flags.

### Basic Analysis
Analyze events from the last N months:
```bash
python main.py --history-months 6
```

### Instagram Profile Lookup
Extract biography and profile data for a specific chapter account:
```bash
python main.py --instagram-user pyladiesbr
```

### Chapter Index Rebuild
Discover and rebuild the full chapter index:
```bash
python main.py --dump-chapters
```

---

## Outputs

All reports, data tables, and Matplotlib visualizations are written to the `outputs/` directory, created automatically on first run.

---

## Case Study: PyLadies Boston

The **PyLadies Boston** chapter is used as the primary benchmark — it is one of the most active chapters globally and produces a consistent event signal for the pipeline to analyze.

### Skill Alignment Chart

Running the pipeline generates a dual-variable bar chart in `outputs/`:

![PyLadies Boston Skill Gap Analysis](outputs/boston_gap_chart.png)

### Analysis

- **Curriculum (pink bars):** The pipeline parsed 8 recent events from the chapter's RSS feed, surfacing both foundational topics (`Python`) and forward-looking curriculum like **"Agentic Coding"** (AI agent workflows) and **"Positron"** (the next-generation Data Science IDE from Posit).
- **Market Demand (blue bars):** The pipeline queries SerpApi's Google Jobs API for active *"Python developer"* postings in Boston, then measures how frequently each taxonomy term appears in those job descriptions.

The gap between these two distributions is the signal — it shows where a chapter's curriculum is aligned with, ahead of, or trailing local employer demand.

---
