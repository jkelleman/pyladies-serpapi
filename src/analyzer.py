import re
from collections import Counter

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
