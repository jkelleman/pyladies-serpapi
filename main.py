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

# 1. Third-party library imports (Alphabetical order)
from dotenv import load_dotenv

# 2. Local application/library imports (Alphabetical order)
from src.analyzer import calculate_gap_analysis
from src.data_fetcher import (
    build_chapter_config,
    fetch_jobs_from_serpapi,
    fetch_pyladies_chapters,
    fetch_pyladies_events,
)
from src.reporter import generate_visualizations, write_markdown_report

# 3. Code execution happens ONLY after ALL imports are completely declared
load_dotenv()


# ------------------ 6. ORCHESTRATION PIPELINE ------------------


def main(api_key=None, history_months=0, dump_chapters=False, instagram_user=None):
    """
    Main pipeline orchestrator.
    """
    # 🌟 O BLOCO DO INSTAGRAM FICA AQUI DENTRO, LOGO NO INÍCIO DA FUNÇÃO
    if instagram_user:
        print(f"[+] Directing request to SerpApi Instagram Profile engine for: @{instagram_user}")
        from src.data_fetcher import fetch_instagram_profile_via_serpapi

        profile_data = fetch_instagram_profile_via_serpapi(instagram_user, api_key)
        if profile_data:
            print("\n================ INSTAGRAM PROFILE DATA ================")
            profile_info = profile_data.get("profile_info", {})
            if profile_info:
                print(f"Name: {profile_info.get('name')}")
                print(f"Biography: {profile_info.get('biography')}")
                print(f"Followers: {profile_info.get('followers')}")
        else:
            print(f"[-] Could not retrieve Instagram data for @{instagram_user}")
        return  # Interrompe o pipeline para não rodar a busca de vagas do Meetup

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

    # Loops through your structured chapter config mapping layer
    for city, group_slug in chapter_config.items():
        # Clean up "pyladies", hyphens, and trailing spaces cleanly
        city_clean = city.replace("pyladies", "").replace("-", " ").strip()

        # Map short acronyms to real cities for accurate Google Jobs routing
        city_map = {
            "cle": "Cleveland",
            "nyc": "New York",
            "la": "Los Angeles",
            "sf": "San Francisco",
            "ams": "Amsterdam",
            "br": "Brazil",  # Fallback for country acronym
            "brasil": "Brazil",  # Intercepts Portuguese spelling to ensure English API mapping
        }

        # Resolve clean query based on abbreviation lookup or defaults (like Boston!)
        city_query = city_map.get(city_clean.lower(), city_clean.capitalize())

        # Safe fallback check for generic global handles
        if not city_query or city_query == "Br":
            city_query = "Brazil"

        print(f"\n>>> Processing {group_slug} chapter (Market: {city_query})...")

        # 1. Fetch data from live APIs
        job_descriptions = fetch_jobs_from_serpapi(city_query, api_key, history_months)
        meetup_events, meetup_source = fetch_pyladies_events(group_slug, history_months)

        # 2. Extract technical skills using taxonomy
        if meetup_events and isinstance(meetup_events[0], dict):
            event_texts = [f"{e.get('title', '')} {e.get('description', '')}" for e in meetup_events]
        else:
            event_texts = [str(e) for e in (meetup_events or [])]

        if job_descriptions and isinstance(job_descriptions[0], dict):
            job_texts = [f"{j.get('title', '')} {j.get('description', '')}" for j in job_descriptions]
        else:
            job_texts = [str(j) for j in (job_descriptions or [])]

        gap_df = calculate_gap_analysis(city_query, job_texts, event_texts)

        if not gap_df.empty:
            os.makedirs(output_dir, exist_ok=True)
            write_markdown_report(gap_df, city_query, output_dir)
            generate_visualizations(gap_df, city_query, output_dir)
            print(f"[+] Outputs updated successfully for chapter: {group_slug}")
        else:
            print(f"[-] No alignment data found to generate reports for {group_slug}.")

    print("\n" + "=" * 60)
    print("Pipeline execution complete! Check the 'outputs/' folder for results.")
    print("=" * 60)


def parse_args():
    parser = argparse.ArgumentParser(description="PyLadies Skill Gap Analyzer")

    # Verifique se estes argumentos já existem:
    parser.add_argument("--api-key", type=str, help="SerpApi API key")
    parser.add_argument("--history-months", type=int, default=3, help="Number of months of history to analyze")
    parser.add_argument("--dump-chapters", action="store_true", help="Dump chapter configurations")
    parser.add_argument("--instagram-user", type=str, help="Instagram username to analyze")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # 🌟 Fixed routing parameter mapping hook:
    main(
        api_key=args.api_key,
        history_months=args.history_months,
        dump_chapters=args.dump_chapters,
        instagram_user=args.instagram_user,  # Pass the Instagram username to the main function
    )
