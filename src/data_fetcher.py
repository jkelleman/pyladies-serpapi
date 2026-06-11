import argparse
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse

from serpapi import Client as SerpApiClient

from src.config import PERSISTED_CHAPTERS_FILE

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


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


def make_cutoff(history_months) -> datetime:
    """
    Calculates the past date cutoff point based on a given number of months.
    Ensures input values are strictly parsed as integers to avoid text/number conflicts.
    """
    # Fallback to a default of 3 months if the argument is missing or None
    if history_months is None:
        history_months = 3

    try:
        # Cast to integer to enforce clean types and prevent 'str' vs 'int' errors
        history_months = int(history_months)
    except (ValueError, TypeError):
        print("[-] Warning: Invalid history_months value received. Defaulting to 3 months.")
        history_months = 3

    # If months are zero or negative, return a far-past date to fetch all available records
    if history_months <= 0:
        return datetime.min.replace(tzinfo=timezone.utc)

    # Calculate target offset threshold securely using timezone-aware UTC datetime
    return datetime.now(timezone.utc) - timedelta(days=history_months * 30)


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


def fetch_instagram_profile_via_serpapi(username: str, api_key: Optional[str] = None) -> Optional[dict]:
    """
    Fetches raw public Instagram profile data and recent post details via SerpApi.
    """
    # Fallback lookup cascade for the API token
    api_key = api_key or os.environ.get("SERPAPI_KEY") or os.environ.get("SERPAPI_API_KEY")

    if not api_key:
        print("[-] Error: Missing SerpApi credential token.")
        return None

    clean_username = username.lstrip("@")

    # Target endpoint configuration mapping
    params = {
        "engine": "instagram_profile",
        "profile_id": clean_username,  # Parameter expected by the Instagram schema
        "api_key": api_key,
    }

    print(f"[+] Routing to: https://serpapi.com/{clean_username}")

    try:
        if GoogleSearch is not None:
            search = GoogleSearch(params)
            results = search.get_dict()
        else:
            client = SerpApiClient(api_key=api_key)
            results = client.search(params).as_dict()

        if isinstance(results, dict) and results.get("error"):
            print(f"[-] SerpApi Error response payload: {results.get('error')}")
            return None

        return results
    except Exception as error:
        print(f"[-] Catastrophic connection failure on Instagram routing execution: {error}")
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
