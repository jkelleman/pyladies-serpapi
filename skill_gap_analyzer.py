"""
Skill-Market Alignment Tool for Pyladies Chapters
Author: Ariana Cursino

This script:
1. Fetches real-time Python jobs from SerpApi (Google Jobs API).
2. Fetches past/current PyLadies events using Meetup RSS or local fallback.
3. Analyzes and maps the "Skill Gap" using a curated skill taxonomy.
4. Generates a clean .csv, a visual gap chart, and a actionable Markdown report.
"""

import argparse
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import pandas as pd
from serpapi import Client as SerpApiClient

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

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
PERSISTED_CHAPTERS_FILE = ".pyladies_chapters.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze the skill gap between local PyLadies chapters and Python job market demand."
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        help="SerpApi API key. Falls back to SERPAPI_API_KEY environment variable if not provided.",
    )
    parser.add_argument(
        "--history-months",
        dest="history_months",
        type=int,
        default=0,
        help="Filter jobs and events to only the last N months. Use 12 for the last year.",
    )
    parser.add_argument(
        "--dump-chapters",
        dest="dump_chapters",
        action="store_true",
        help="Fetch the Pyladies Meetup topic page and print discovered chapter slugs.",
    )
    return parser.parse_args()


def parse_date_string(date_string: str) -> Optional[datetime]:
    if not date_string:
        return None
    try:
        return parsedate_to_datetime(date_string)
    except Exception:
        pass

    try:
        if date_string.endswith("Z"):
            date_string = date_string[:-1] + "+00:00"
        return datetime.fromisoformat(date_string)
    except Exception:
        return None


def make_cutoff(history_months: int) -> Optional[datetime]:
    if history_months <= 0:
        return None
    return datetime.utcnow() - timedelta(days=history_months * 30)


# ------------------ 2. Data Acquisition ------------------


def fetch_jobs_from_serpapi(city: str, api_key: str, history_months: int = 0) -> list:
    """Fetches Python job listings from SerpApi (Google Jobs API) for a given city."""
    if not api_key:
        print(f"[-] No SerpApi API key provided. Skipping job data fetch for {city}")
        print("(no API key). Returning empty job set.")
        return []

    cutoff = make_cutoff(history_months)

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
        filtered_jobs = []
        for job in jobs:
            if cutoff is None:
                filtered_jobs.append(job)
                continue

            job_date = None
            for key in [
                "date",
                "posted_at",
                "posted_date",
                "created_at",
                "published_at",
                "publication_date",
            ]:
                if key in job and job[key]:
                    job_date = parse_date_string(str(job[key]))
                    if job_date:
                        break

            if job_date is None:
                filtered_jobs.append(job)
            elif job_date >= cutoff:
                filtered_jobs.append(job)

        descriptions = [job.get("description", "") for job in filtered_jobs if job.get("description")]
        print(
            f"[+] Extracted descriptions from {len(descriptions)} job postings "
            f"(filtered to last {history_months} months)."
            if cutoff
            else f"[+] Extracted descriptions from {len(descriptions)} job postings."
        )
        return descriptions
    except Exception as e:
        print(f"[-] SerpApi fetch failed: {e}. No job data returned for {city}.")
        return []


def fetch_pyladies_events(group_slug: str, history_months: int = 0) -> tuple:
    """
    Fetch PyLadies events from the Meetup RSS feed for the chapter.

    Returns a tuple: (events_list, source_tag) where source_tag is one of
    'meetup_rss' or 'none'.
    """
    cutoff = make_cutoff(history_months)
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
            pub_date_elem = item.find("pubDate")
            pub_date = (
                parse_date_string(pub_date_elem.text.strip())
                if pub_date_elem is not None and pub_date_elem.text
                else None
            )

            if cutoff is not None and pub_date is not None and pub_date < cutoff:
                continue

            events.append(f"{title} {desc}")

        print(
            f"[+] Successfully parsed {len(events)} events from RSS " f"(filtered to last {history_months} months)."
            if cutoff
            else f"[+] Successfully parsed {len(events)} events from RSS."
        )
        return events, "meetup_rss"
    except Exception as e:
        print(f"[-] Meetup RSS feed unavailable ({e}). No curriculum events returned for {group_slug}.")
        return [], "none"


def load_persisted_chapter_slugs() -> list:
    if not os.path.exists(PERSISTED_CHAPTERS_FILE):
        return {}
    try:
        with open(PERSISTED_CHAPTERS_FILE, "r", encoding="utf-8") as handle:
            import json

            data = json.load(handle)
        # Support legacy format (list of slugs) and new format (dict of slug->meta)
        if isinstance(data, list):
            return {slug: {"source": "persisted"} for slug in data if isinstance(slug, str)}
        if isinstance(data, dict):
            return data
        return {}
    except Exception as e:
        print(f"[-] Failed to load persisted chapter slugs: {e}")
        return {}


def fetch_instagram_profile_via_serpapi(username: str, api_key: Optional[str] = None):
    api_key = api_key or os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        return None
    try:
        client = SerpApiClient(api_key=api_key)
        params = {"engine": "instagram_profile", "username": username, "api_key": api_key}
        results = client.search(params).as_dict()
        return results
    except Exception:
        # try GoogleSearch wrapper if available
        try:
            if GoogleSearch is not None:
                search = GoogleSearch({"engine": "instagram_profile", "username": username, "api_key": api_key})
                return search.get_dict()
        except Exception:
            pass
    return None


def save_persisted_chapter_slugs(slugs) -> None:
    """Accepts either a list of slug strings or a dict mapping slug->meta and persists metadata.

    For any newly provided slug (from a list), the function will attempt to enrich with
    Instagram profile info (best-effort) and store a mapping: slug -> {source, instagram, added_at}.
    """
    try:
        import json
        from datetime import datetime

        existing = load_persisted_chapter_slugs() or {}

        # Normalize incoming slugs into a dict
        if isinstance(slugs, list):
            incoming = {}
            for slug in slugs:
                incoming[slug] = {"source": "serpapi", "added_at": datetime.utcnow().isoformat()}
        elif isinstance(slugs, dict):
            incoming = slugs
        else:
            print("[-] Unsupported slugs payload for persistence.")
            return

        # Merge and enrich
        merged = dict(existing)
        for slug, meta in incoming.items():
            if slug in merged:
                # keep existing metadata but update source if missing
                merged[slug].setdefault("source", meta.get("source", "serpapi"))
            else:
                merged[slug] = {"source": meta.get("source", "serpapi"), "added_at": meta.get("added_at")}
                # best-effort: try to fetch Instagram profile using slug as username
                try:
                    insta = fetch_instagram_profile_via_serpapi(slug)
                    if insta:
                        merged[slug]["instagram"] = insta
                except Exception:
                    pass

        with open(PERSISTED_CHAPTERS_FILE, "w", encoding="utf-8") as handle:
            json.dump(merged, handle, indent=2, ensure_ascii=False)

        print(f"[+] Saved {len(merged)} discovered chapter slugs to {PERSISTED_CHAPTERS_FILE}.")
    except Exception as e:
        print(f"[-] Failed to persist chapter slugs: {e}")


def fetch_chapters_via_serpapi(api_key: Optional[str] = None, num: int = 100) -> list:
    """Use SerpApi (Google) to find Meetup group slugs related to PyLadies.

    Returns a list of unique slugs (e.g. 'pyladies-boston', 'houston_pyladies').
    """
    api_key = api_key or os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        print("[-] No SerpApi API key available for SerpApi-based chapter discovery.")
        return []

    print("[+] Fetching chapter list via SerpApi (Google index)...")

    params = {
        "engine": "google",
        "q": "site:meetup.com pyladies",
        "hl": "en",
        "num": num,
        "api_key": api_key,
    }

    try:
        client = SerpApiClient(api_key=api_key)
        results = client.search(params).as_dict()
    except Exception:
        # Try the older GoogleSearch wrapper if available
        try:
            if GoogleSearch is not None:
                search = GoogleSearch(params)
                results = search.get_dict()
            else:
                raise
        except Exception as e:
            print(f"[-] SerpApi query failed: {e}")
            return []

    organic = results.get("organic_results", []) or []
    slugs = set()

    for item in organic:
        link = item.get("link") or item.get("displayed_link") or ""
        if not link:
            continue

        # Normalize and extract path segment after meetup.com/
        m = re.search(r"meetup\.com/(?:[A-Za-z\-]+/)?([A-Za-z0-9_\-]+)", link)
        if not m:
            continue
        slug = m.group(1)
        slug_l = slug.lower()

        # Keep only PyLadies-related groups (most slugs contain 'pyladies')
        if "pyladies" not in slug_l:
            continue

        # Filter out known non-group paths
        if slug_l in {"topics", "apps", "find", "explore", "lp", "events"}:
            continue

        slugs.add(slug)

    print(f"[+] SerpApi discovered {len(slugs)} candidate chapter slugs.")
    return sorted(slugs)


def build_chapter_config(api_key: Optional[str] = None) -> dict:
    persisted = load_persisted_chapter_slugs()
    if persisted:
        print(f"[+] Loaded {len(persisted)} persisted chapter slugs.")
        return {slug: slug for slug in persisted}

    discovered = fetch_chapters_via_serpapi(api_key=api_key)
    if discovered:
        save_persisted_chapter_slugs(discovered)
        return {slug: slug for slug in discovered}

    print("[-] No chapter slugs available; please populate .pyladies_chapters.json or run --dump-chapters.")
    return {}


def fetch_pyladies_chapters(topic_url: str = "https://www.meetup.com/pt-BR/topics/pyladies/all/") -> list:
    """Fetch meetup chapter slugs from the Pyladies topic listing page."""
    print(f"[+] Fetching chapter list from {topic_url}")
    try:
        with urllib.request.urlopen(topic_url, timeout=15) as response:
            page_html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[-] Failed to fetch Meetup topic page: {e}")
        return []

    slugs = set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', page_html):
        parsed = urlparse(href)
        path = parsed.path.strip("/")
        if not path:
            continue
        if path.startswith("pt-BR/"):
            path = path.split("/", 1)[1]
        if "/" in path:
            path = path.split("/", 1)[0]
        if not path or "topics" in path or "events" in path or "groups" in path:
            continue
        if "pyladies" not in path.lower():
            continue
        if re.match(r"^[a-zA-Z0-9_-]+$", path):
            slugs.add(path)

    # If static HTML parsing found no slugs, try rendering the page with Playwright
    # If static HTML parsing found no slugs, try SerpApi index-based discovery first
    if not slugs:
        serpapi_slugs = fetch_chapters_via_serpapi()
        if serpapi_slugs:
            print("[+] Using SerpApi-discovered slugs.")
            return serpapi_slugs

    if not slugs and sync_playwright is not None:
        print("[+] No slugs found in static HTML — trying Playwright render fallback...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(topic_url, timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass
                rendered = page.content()
                browser.close()

            for href in re.findall(r'href=["\']([^"\']+)["\']', rendered):
                parsed = urlparse(href)
                path = parsed.path.strip("/")
                if not path:
                    continue
                if path.startswith("pt-BR/"):
                    path = path.split("/", 1)[1]
                if "/" in path:
                    path = path.split("/", 1)[0]
                if not path or "topics" in path or "events" in path or "groups" in path:
                    continue
                if "pyladies" not in path.lower():
                    continue
                if re.match(r"^[a-zA-Z0-9_-]+$", path):
                    slugs.add(path)
        except Exception as e:
            print(f"[-] Playwright render fallback failed: {e}")
            print("To enable this fallback, install Playwright: ")
            print("`pip install playwright` and run `playwright install`.")

    return sorted(slugs)


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

    Aggregates rows by `Skill` to avoid duplicate skill labels coming from multiple
    taxonomy categories (e.g., `Flask` appearing under both Web Frameworks and
    Software Engineering). Aggregation takes the max observed percentage for
    Market and Curriculum coverage per skill before computing the Gap.
    """
    # Aggregate by Skill to ensure unique labels in the chart
    if "Skill" in df.columns:
        agg = df.groupby("Skill")[["Market Demand (%)", "Curriculum Coverage (%)"]].max().reset_index()
        agg["Gap (%)"] = agg["Market Demand (%)"] - agg["Curriculum Coverage (%)"]
    else:
        agg = df.copy()

    # Filter to show only skills that have at least some market demand or curriculum coverage
    active_skills = agg[(agg["Market Demand (%)"] > 0) | (agg["Curriculum Coverage (%)"] > 0)]
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


def main(api_key=None, history_months=0, dump_chapters=False):
    if dump_chapters:
        slugs = fetch_pyladies_chapters()
        if not slugs:
            print("[-] No chapter slugs discovered.")
            return

        print("[+] Discovered Pyladies chapter slugs:")
        for slug in slugs:
            print(f"- {slug}")

        print("\nCopy these slugs into .pyladies_chapters.json or use them to build a chapter mapping.")
        return

    # Prefer CLI-provided API key, then environment variable.
    api_key = api_key or os.environ.get("SERPAPI_API_KEY")
    if api_key:
        print("[+] Using SerpApi API key from command-line or environment.")
    else:
        print("[-] No SerpApi API key provided. Skipping job data fetch for jobs; job data will be empty.")

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    chapter_config = build_chapter_config(api_key=api_key)

    print("=" * 60)
    print("Starting PyLadies Skill-Market Alignment Pipeline")
    print("=" * 60)

    for city, group_slug in chapter_config.items():
        print(f"\n>>> Processing {city} chapter...")

        # 1. Fetch data
        job_descriptions = fetch_jobs_from_serpapi(city, api_key, history_months)
        meetup_events, meetup_source = fetch_pyladies_events(group_slug, history_months)

        # 2. Run analysis
        gap_df = calculate_gap_analysis(city, job_descriptions, meetup_events)

        # Add provenance/source column for this chapter's curriculum data
        gap_df["Source"] = meetup_source

        # 3. Save CSV
        csv_path = os.path.join(output_dir, f"{city.lower().replace(' ', '_')}_gap_data.csv")
        gap_df.to_csv(csv_path, index=False)
        print(f"[+] Saved raw analysis data to: {csv_path} (Source: {meetup_source})")

        # 4. Generate visual plot
        generate_visualizations(gap_df, city, output_dir)

        # 5. Generate Markdown Report
        write_markdown_report(gap_df, city, output_dir)

    print("\n" + "=" * 60)
    print("Pipeline execution complete! Check the 'outputs/' folder for results.")
    print("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    main(api_key=args.api_key, history_months=args.history_months, dump_chapters=args.dump_chapters)
