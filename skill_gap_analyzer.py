"""
Skill-Market Alignment Tool for Pyladies Chapters
Author: Ariana Cursino

This script:
1. Fetches real-time Python jobs from SerpApi (Google Jobs API).
2. Fetches past/current Pyladies events (using Meetup, Linkedin, or local fallback).
3. Analyzes and maps the "Skill Gap"using a curated skill taxonomy.
4. Generates a clean .csv, a visual gap chart, and a actionable Markdown report.
"""

import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
from serpapi import Client as SerpApiClient

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# ------------------ 1.Configuration and Skill Taxonomy ------------------
# A curated skill taxonomy based on common Python job requirements and Pyladies event topics
SKILL_TAXONOMY = {
    "Web Frameworks": ["Django", "Flask", "FastAPI", "Tornado", "Sanic", "Streamlit"],
    "Data & ML": [
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "Keras",
        "XGBoost",
        "Polars",
        "Jupyter",
        "Matplotlib",
        "Seaborn",
        "Plotly",
    ],
    "Cloud & DevOps": [
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "Terraform",
        "CI/CD",
    ],
    "Testing & QA": ["PyTest", "UnitTest", "Selenium", "Cypress", "Test Automation"],
    "Data Engineering": [
        "Airflow",
        "Luigi",
        "Kafka",
        "Spark",
        "Hadoop",
        "ETL",
        "Data Pipelines",
    ],
    "Software Engineering": [
        "Flask",
        "Django",
        "FastAPI",
        "OOP",
        "Design Patterns",
        "Clean Code",
        "Code Reviews",
    ],
    "Scripting & Automation": ["Bash", "PowerShell", "Ansible", "Fabric", "Invoke"],
    "Version Control": ["Git", "GitHub", "GitLab", "Bitbucket"],
    "Databases": ["SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"],
    "APIs & Microservices": ["REST", "GraphQL", "gRPC", "OpenAPI", "Swagger"],
    "Other": [
        "Python",
        "OOP",
        "Functional Programming",
        "Asyncio",
        "Multithreading",
        "Multiprocessing",
        "Regular Expressions",
        "Logging",
        "Debugging",
        "Performance Optimization",
    ],
}

ALL_SKILLS = [skill for sublist in SKILL_TAXONOMY.values() for skill in sublist]

# ------------------ 1.b Default Chapter Configuration ------------------
CITIES_CONFIG = {"São Paulo": "pyladies-sao-paulo", "Rio de Janeiro": "pyladies-rio"}

# ------------------ 2. Data Acquisition ------------------


def fetch_jobs_from_serpapi(city: str, api_key: str) -> list:
    """Fetches Python job listings from SerpApi (Google Jobs API) for a given city."""
    if not api_key:
        print(f"[-] No SerpApi API key provided. Skipping job data fetch for {city} (Demo Mode).")
        return get_mock_jobs(city)

    print(f"[+] Fetching Python jobs for {city} from SerpApi...")
    try:
        params = {
            "engine": "google_jobs",
            "q": f"Python Developer in {city}",
            "hl": "en",
            "api_key": api_key,
        }

        if GoogleSearch is not None:
            search = GoogleSearch(params)
            results = search.get_dict()
        else:
            client = SerpApiClient(api_key=api_key)
            results = client.search(params).as_dict()

        jobs = results.get("jobs_results", [])
        descriptions = [job.get("description", "") for job in jobs if job.get("description")]
        print(f"[+] Extracted descriptions from {len(descriptions)} job postings.")
        return descriptions
    except Exception as e:
        print(f"[-] SerpApi fetch failed: {e}. Falling back to mock data.")
        return get_mock_jobs(city)


def fetch_pyladies_events(group_slug: str, source: str = "rss") -> list:
    """
    Fetch PyLadies events from a chosen source. source: "rss" (Meetup RSS, default) or "linkedin".
    """
    if source not in ("rss", "linkedin"):
        print(f"[!] Unknown source '{source}'. Falling back to RSS.")
        source = "rss"

    if source == "rss":
        print(f"[+] Fetching public RSS feed for PyLadies group: {group_slug}...")
        rss_url = f"https://www.meetup.com/{group_slug}/events/rss/"

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        req = urllib.request.Request(rss_url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()

            root = ET.fromstring(xml_data)
            events = []
            for item in root.findall(".//item"):
                title = item.find("title").text or ""
                desc = item.find("description").text or ""
                events.append(f"{title} {desc}")

            print(f"[+] Successfully parsed {len(events)} events from RSS.")
            return events
        except Exception as e:
            print(f"[-] Meetup RSS feed unavailable ({e}). Using mock curriculum data.")
            return get_mock_curriculum(group_slug)

    elif source == "linkedin":
        return fetch_pyladies_events_linkedin(group_slug)


def fetch_pyladies_events_linkedin(group_slug: str) -> list:
    """
    Fetch PyLadies events from LinkedIn (requires access token and org ID). Falls back
    to mock data if credentials are missing or request fails.
    """
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    org_id = os.environ.get("LINKEDIN_ORG_ID")  # e.g., "123456"

    if not token or not org_id:
        print("[!] LinkedIn credentials not found. Falling back to mock data.")
        return get_mock_curriculum(group_slug)

    # NOTE: The exact LinkedIn API endpoint may differ depending on your app permissions
    url = f"https://api.linkedin.com/v2/events?q=owner&owners=urn:li:organization:{org_id}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        events = []
        for item in data.get("elements", []):
            title = item.get("name", "")
            start = item.get("startDate", "")
            location = item.get("location", "")
            events.append(f"{title} - {start} {location}".strip())
        print(f"[+] Retrieved {len(events)} LinkedIn events.")
        return events
    except Exception as e:
        print(f"[-] LinkedIn fetch failed: {e}. Using mock data.")
        return get_mock_curriculum(group_slug)


# ------------------ 3. MOCK DATA (For Demo Mode/Fallbacks) ------------------


def get_mock_jobs(city: str) -> list:
    """
    Returns sample job descriptions with realistic skill distributions.
    """
    return [
        "We are looking for a Python Developer experienced with Django, PostgreSQL, and AWS. Docker is a plus.",
        "Senior Data Scientist role. Must know Pandas, NumPy, PyTorch, and SQL. Experience with Jupyter is required.",
        "Backend Engineer: FastAPI, REST APIs, Docker, and CI/CD. AWS or GCP cloud experience is highly preferred.",
        "Python Developer with strong SQL, Git, and Pytest skills. Django or Flask experience is a benefit.",
        "Data Engineer: Building pipelines with Pandas, Polars, and PostgreSQL. Deploying on AWS using Docker.",
    ] * 5  # Multiply to simulate a larger dataset


def get_mock_curriculum(group_slug: str) -> list:
    """
    Returns sample past workshops for PyLadies chapters.
    """
    return [
        "Intro to Python Basics and Git version control",
        "Data Analysis 101: Getting started with Pandas and Jupyter Notebooks",
        "Building your first web application using Flask and SQLite",
        "PyLadies Hackathon: Collaborative coding with GitHub",
        "Introduction to SQL databases and basic queries using Python",
    ]


# ------------------ 4. ANALYSIS ENGINE  ------------------


def extract_skills(text_list: list) -> Counter:
    """
    Scans text blocks and counts occurrences of skills from the taxonomy.
    """
    counts = Counter()
    for text in text_list:
        if not text:
            continue
        lower_text = text.lower()
        for skill in ALL_SKILLS:
            # Word boundary regex to avoid partial matches (e.g., matching "Git" in "Digital")
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pattern, lower_text):
                counts[skill] += 1
    return counts


def calculate_gap_analysis(city: str, job_texts: list, meetup_texts: list) -> pd.DataFrame:
    """
    Computes the alignment and gap between job market demand and curriculum coverage.

    The gap is calculated as:
    $$Gap = P_{market} - P_{curriculum}$$

    Where:
    - $$P_{market}$$ is the percentage of job descriptions mentioning the skill.
    - $$P_{curriculum}$$ is the percentage of workshops covering the skill.
    """
    market_counts = extract_skills(job_texts)
    curr_counts = extract_skills(meetup_texts)

    total_jobs = len(job_texts) or 1
    total_events = len(meetup_texts) or 1

    rows = []
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            m_count = market_counts.get(skill, 0)
            c_count = curr_counts.get(skill, 0)

            m_pct = m_count / total_jobs
            c_pct = c_count / total_events
            gap = m_pct - c_pct

            rows.append(
                {
                    "Category": category,
                    "Skill": skill,
                    "Market Demand (%)": round(m_pct * 100, 1),
                    "Curriculum Coverage (%)": round(c_pct * 100, 1),
                    "Gap (%)": round(gap * 100, 1),
                }
            )

    return pd.DataFrame(rows)


# ------------------ 5. VISUALIZATION & REPORTING ------------------
def generate_visualizations(df: pd.DataFrame, city: str, output_dir: str):
    """
    Generates a side-by-side bar chart showing the biggest skill gaps.
    """
    # Filter to show only skills that have at least some market demand or curriculum coverage
    active_skills = df[(df["Market Demand (%)"] > 0) | (df["Curriculum Coverage (%)"] > 0)]
    active_skills = active_skills.sort_values("Gap (%)", ascending=False).head(12)

    if active_skills.empty:
        print(f"[-] No overlapping active skills to plot for {city}.")
        return

    plt.figure(figsize=(12, 7))
    x = range(len(active_skills))
    width = 0.35

    plt.bar(
        [i - width / 2 for i in x],
        active_skills["Market Demand (%)"],
        width,
        label="Market Demand (%)",
        color="#1f77b4",
    )
    plt.bar(
        [i + width / 2 for i in x],
        active_skills["Curriculum Coverage (%)"],
        width,
        label="Curriculum Coverage (%)",
        color="#e377c2",
    )

    plt.xlabel("Skills", fontsize=12)
    plt.ylabel("Frequency (%)", fontsize=12)
    plt.title(
        f"Skill Gap Analysis: PyLadies {city} vs Local Job Market",
        fontsize=14,
        fontweight="bold",
    )
    plt.xticks(x, active_skills["Skill"], rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(output_dir, f"{city.lower().replace(' ', '_')}_gap_chart.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"[+] Saved visualization chart to: {plot_path}")


def write_markdown_report(df: pd.DataFrame, city: str, output_dir: str):
    """
    Generates a beautifully formatted markdown report with chapter recommendations."""
    report_path = os.path.join(output_dir, f"{city.lower().replace(' ', '_')}_report.md")

    # Sort by biggest gap (high market demand, low curriculum coverage)
    top_recommendations = df.sort_values("Gap (%)", ascending=False).head(5)

    # Sort by well-aligned skills
    aligned_skills = df[df["Gap (%)"].abs() <= 15].sort_values("Market Demand (%)", ascending=False).head(5)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Skill-Market Alignment Report: PyLadies {city}\n\n")
        f.write(
            "This report evaluates local Python job postings against the past workshop topics "
            "taught by the local PyLadies chapter to find opportunities for new curriculum "
            "design.\n\n"
        )

        f.write("## 🚀 Top 5 Curriculum Recommendations\n")
        f.write(
            "These skills are highly requested by employers but have been underrepresented "
            "in recent workshops. Consider designing a workshop or study group around them:\n\n"
        )
        for _, row in top_recommendations.iterrows():
            f.write(
                f"- **{row['Skill']}** ({row['Category']}): Market Demand is at "
                f"**{row['Market Demand (%)']}%**, but Chapter Coverage is only "
                f"**{row['Curriculum Coverage (%)']}%** (Gap: **+{row['Gap (%)']}%**).\n"
            )

        f.write("\n## 🎉 Well-Aligned Skills\n")
        f.write("Great job! These in-demand skills are already well-covered in your curriculum:\n\n")
        for _, row in aligned_skills.iterrows():
            f.write(
                f"- **{row['Skill']}** (Market: {row['Market Demand (%)']}%, "
                f"Curriculum: {row['Curriculum Coverage (%)']}%)\n"
            )

        f.write("\n## 📊 Complete Skill Matrix\n\n")
        f.write("| Category | Skill | Market Demand (%) | Curriculum Coverage (%) | Gap (%) |\n")
        f.write("| --- | --- | ---: | ---: | ---: |\n")
        for _, row in df.sort_values(["Category", "Gap (%)"], ascending=[True, False]).iterrows():
            f.write(
                f"| {row['Category']} | {row['Skill']} | "
                f"{row['Market Demand (%)']}% | {row['Curriculum Coverage (%)']}% | "
                f"{row['Gap (%)']}% |\n"
            )

    print(f"[+] Saved written report to: {report_path}")


# ------------------ 6. ORCHESTRATION PIPELINE ------------------


def main():
    # Grab SerpApi key from environment variables
    api_key = os.environ.get("SERPAPI_API_KEY")

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Starting PyLadies Skill-Market Alignment Pipeline")
    print("=" * 60)

    for city, group_slug in CITIES_CONFIG.items():
        print(f"\n>>> Processing {city} chapter...")

        # 1. Fetch data
        job_descriptions = fetch_jobs_from_serpapi(city, api_key)
        meetup_events = fetch_pyladies_events(group_slug)

        # 2. Run analysis
        gap_df = calculate_gap_analysis(city, job_descriptions, meetup_events)

        # 3. Save CSV
        csv_path = os.path.join(output_dir, f"{city.lower().replace(' ', '_')}_gap_data.csv")
        gap_df.to_csv(csv_path, index=False)
        print(f"[+] Saved raw analysis data to: {csv_path}")

        # 4. Generate visual plot
        generate_visualizations(gap_df, city, output_dir)

        # 5. Generate Markdown Report
        write_markdown_report(gap_df, city, output_dir)

    print("\n" + "=" * 60)
    print("Pipeline execution complete! Check the 'outputs/' folder for results.")
    print("=" * 60)


if __name__ == "__main__":
    main()
