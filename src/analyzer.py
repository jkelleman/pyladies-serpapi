import re
from collections import Counter
from typing import Dict, List

import pandas as pd

from src.config import ALL_SKILLS, SKILL_TAXONOMY


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


def align_instagram_events_with_market(
    instagram_data: dict, market_jobs: List[dict], skill_taxonomy: Dict[str, List[str]]
) -> dict:
    """
    Extracts tech keywords from Instagram metrics and maps alignment with local job profiles.
    """
    # 1. Harvest texts from profile bio and post captions
    profile_info = instagram_data.get("profile_info", {})
    source_text = profile_info.get("biography", "") + " "

    # Concatenate captions from recent posts
    for post in instagram_data.get("posts", []):
        source_text += post.get("caption", "") + " "

    # 2. Extract mentioned technologies using regular expressions
    detected_skills = set()
    for category, keywords in skill_taxonomy.items():
        for keyword in keywords:
            # Word boundary matching prevents partial word triggers
            if re.search(r"\b" + re.escape(keyword) + r"\b", source_text, re.IGNORECASE):
                detected_skills.add(keyword)

    # 3. Process jobs list data to check against market requirements
    market_demand_counts = {}
    for job in market_jobs:
        description = job.get("description", "")
        for skill in detected_skills:
            if re.search(r"\b" + re.escape(skill) + r"\b", description, re.IGNORECASE):
                market_demand_counts[skill] = market_demand_counts.get(skill, 0) + 1

    # 4. Generate alignment scorecard metrics
    return {
        "chapter_skills_taught": list(detected_skills),
        "aligned_market_demand": market_demand_counts,
        "unmatched_skills_count": len(detected_skills) - len(market_demand_counts),
    }
