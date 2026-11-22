#                   TASK 1
# 1) Report the total number of classified ASes.
# 2) Report the number of classified ASes in each category.
# 3) Report each category's percentage of the yearly total
# 4) Present the distributions for 2015 and 2021 (i.e., output 2 bar charts or pie charts)
from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "processed"
FIGURES_DIR = REPO_ROOT / "figures"


def task1():
    filePaths = {
        "2015": DATA_DIR / "as2types_20150801_clean.csv",
        "2021": DATA_DIR / "as2types_20210401_clean.csv",
    }
    categoryPercentages = {}

    for year, filePath in filePaths.items():
        lineCount = 0
        categoryCount = {
            "Transit/Access": 0,
            "Content": 0,
            "Enterprise": 0,
        }

        with open(filePath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("asn"):
                    continue

                lineCount += 1
                for category in categoryCount:
                    if category in line:
                        categoryCount[category] += 1
                        break

        categoryPercentage = {
            category: categoryCount[category] / lineCount * 100
            if lineCount > 0
            else 0
            for category in categoryCount
        }
        categoryPercentages[year] = categoryPercentage

        print(f"-------------------------------- {year} --------------------------------")
        print("Total Number of Classified ASes:", lineCount)
        for category in categoryCount:
            print(
                f"# of {category} ASes:",
                categoryCount[category],
                "\t Percent:",
                categoryPercentage[category],
            )
        print()

    categories = ["Transit/Access", "Content", "Enterprise"]
    yearData = [
        ("2015", [categoryPercentages["2015"][category] for category in categories]),
        ("2021", [categoryPercentages["2021"][category] for category in categories]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for ax, (year, percentages) in zip(axes, yearData):
        bars = ax.bar(categories, percentages, color=["tab:blue", "tab:orange", "tab:green"])
        ax.set_title(f"AS Classification Distribution ({year})")
        ax.set_ylabel("Percentage of Classified ASes")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=20)

        for bar, percentage in zip(bars, percentages):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{percentage:.1f}%",
                ha="center",
                va="bottom",
            )

    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    outputPath = FIGURES_DIR / "graph1_year_distributions.png"
    fig.savefig(outputPath, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"\nSaved distribution chart: {outputPath}")


if __name__ == "__main__":
    task1()