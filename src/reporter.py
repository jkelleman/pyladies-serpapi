import os

import matplotlib.pyplot as plt
import pandas as pd


def generate_visualizations(df: pd.DataFrame, city: str, output_dir: str):
    """
    Generates a clean comparative bar chart comparing PyLadies curriculum against job market demand.
    """
    if df is None or df.empty:
        print("[-] Warning: No alignment data available to plot.")
        return

    chart_path = os.path.join(output_dir, f"{city.lower().replace(' ', '_')}_gap_chart.png")

    df = df.copy()
    df["Market Demand (%)"] = df.get("Market Demand (%)", 0).fillna(0)
    df["Curriculum Coverage (%)"] = df.get("Curriculum Coverage (%)", 0).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 6))

    if "Skill" in df.columns:
        plot_x = "Skill"
    elif "Skills" in df.columns:
        plot_x = "Skills"
    else:
        print("[-] Warning: No skill label column found for plotting.")
        return

    df.plot(
        kind="bar", x=plot_x, y=["Market Demand (%)", "Curriculum Coverage (%)"], ax=ax, color=["#1f77b4", "#e377c2"]
    )

    ax.set_title(f"Skill Gap Analysis: PyLadies {city} vs Local Job Market", fontsize=12, fontweight="bold")
    ax.set_ylabel("Frequency (%)", fontsize=10)
    ax.set_xlabel(plot_x, fontsize=10)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[+] Clean analytical chart saved successfully to: {chart_path}")


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
