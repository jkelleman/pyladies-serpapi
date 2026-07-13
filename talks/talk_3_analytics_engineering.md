# Talk Proposal: Introduction to Analytics Engineering: Bridging Software Best Practices with Data Science

## 📋 Overview
Many data scientists and analysts start their work in standalone Jupyter Notebooks, but struggle when transitioning to collaborative, production-grade data pipelines. Enter Analytics Engineering! In this talk, we’ll discuss how to bring software engineering best practices—such as version control (Git), automated testing, clean modeling, and semantic layers—directly into your SQL and Python data analyses.

## 🎯 Target Audience
- Data Analysts and Data Scientists looking to scale up their workflows
- Python Developers transitioning into Data Engineering or Analytics Engineering
- Anyone curious about how modern data teams build scalable, reliable data layers

## 🛠️ Key Takeaways
- **What is Analytics Engineering?:** Understanding the unique role that sits between Data Engineering and Data Science.
- **Software Best Practices for Data:** Applying Git, modular designs, and testing directly to SQL and data schemas.
- **The Power of Semantic Layers:** Demystifying how modern organizations define and govern key business metrics to ensure consistency.

## 🕒 Suggested Agenda (45 Minutes)
- **00:00 - 00:15 | The Shift to Analytics Engineering:** Jupyter Notebook chaos vs. Git-managed analytical databases.
- **00:15 - 00:35 | Best Practices Walkthrough:** Demonstrating how to use modern analytical layers, dbt, or semantic metrics to ensure data quality and lineage.
- **00:35 - 00:45 | Q&A & Open Discussion:** Navigating the modern data stack career path.

## 🔗 Connection to Portfolio Repositories
- [semantic-metrics-modeling-assistant](https://github.com/jkelleman/semantic-metrics-modeling-assistant)
- [rental-bike-sharing](https://github.com/jkelleman/rental-bike-sharing)

---

## 🛠️ Attendee Pre-requisites & Setup Guide
- **Python 3.10+** and **Git** installed on your system.
- Basic knowledge of SQL (SELECT statements, JOINs, and aggregates).
- (Optional) Install `dbt-core` and `dbt-duckdb`: `pip install dbt-core dbt-duckdb`
- Recommended tool: **VS Code** with the Power User dbt extension.

## 📢 Promotion & Marketing Copy
**Meetup Description:**
Tired of Jupyter Notebook chaos and fragile data pipelines? Join us for an introduction to **Analytics Engineering**! Learn how modern data teams bring software engineering best practices—like Git version control, modular modeling, automated testing, and semantic layers—directly into SQL and Python analyses.

**Hashtags:**
#PyLadies #Python #AnalyticsEngineering #dbt #SQL #DataScience #DataQuality

## 💬 Interactive Audience Engagement Plan
- **Icebreaker Poll:** "Where does most of your data analysis live? (Jupyter Notebooks / Local CSVs / Cloud Data Warehouse / Excel)"
- **Interactive Checkpoint:** Show a raw, unorganized SQL query and challenge the audience to identify how they would refactor it into clean, modular, and testable dbt models.

## 💻 Interactive Code Sandbox Link
- **Status:** Under development (see preparation roadmap in [README.md](./README.md)). Once configured, you can run dbt models locally in your browser by launching a pre-configured dbt sandbox via [GitHub Codespaces](https://github.com/features/codespaces) on the [semantic-metrics-modeling-assistant](https://github.com/jkelleman/semantic-metrics-modeling-assistant) repository.
