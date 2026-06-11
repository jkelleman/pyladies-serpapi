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

from src.analyzer import align_instagram_events_with_market, calculate_gap_analysis
from src.data_fetcher import (
    build_chapter_config,
    fetch_instagram_profile_via_serpapi,
    fetch_jobs_from_serpapi,
    fetch_pyladies_chapters,
    fetch_pyladies_events,
)
from src.reporter import generate_visualizations, write_markdown_report

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

    if args.instagram_user:
        print("[+] Launching localized Instagram-to-Job alignment mapping sequence...")

        # Fetch Instagram data via SerpApi
        insta_payload = fetch_instagram_profile_via_serpapi(args.instagram_user, api_key=args.api_key)

        if insta_payload:
            # Fetch mock or live job market data array for comparison
            # (Assuming 'sample_city_jobs' variable exists from your pipeline configurations)
            sample_city_jobs = []

            from src.config import SKILL_TAXONOMY

            alignment_report = align_instagram_events_with_market(insta_payload, sample_city_jobs, SKILL_TAXONOMY)

            print("\n================= ALIGNMENT METRICS REPORT =================")
            print(f"Technologies found in community events: {alignment_report['chapter_skills_taught']}")
            print(f"Market validation matching frequency: {alignment_report['aligned_market_demand']}")
            print("============================================================\n")
        else:
            print("[-] Pipeline halted due to empty data ingestion layer metrics.")
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


def parse_args():
    parser = argparse.ArgumentParser(description="PyLadies Skill Gap Analyzer")

    # Verifique se estes argumentos já existem:
    parser.add_argument("--api-key", type=str, help="SerpApi API key")
    parser.add_argument("--history-months", type=int, default=3, help="Number of months of history to analyze")
    parser.add_argument("--dump-chapters", action="store_true", help="Dump chapter configurations")

    # 🌟 ADICIONE ESTA LINHA QUE ESTÁ FALTANDO:
    parser.add_argument("--instagram-user", type=str, help="Instagram username to analyze")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(api_key=args.api_key, history_months=args.history_months, dump_chapters=args.dump_chapters)
