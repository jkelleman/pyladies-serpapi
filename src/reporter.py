import os

import matplotlib.pyplot as plt
import pandas as pd


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
