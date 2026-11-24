#                               TASK 4
# 1) Use the 2024 relationship graph to assign each observed AS exactly one of the 3 structural labels (customer-serving, peering edge, or stubs/muli-homed ASes)
# 2) On ASes in both the 2021 classification file and 2024 relationship graph, make a 3x3 contingency table (business label by structural label)
#       a) Give the matched sample size and excluded/unmatched counts
# 3) Plot the structural-role percentages conditioned on each business class (e.g., a normalized stacked bar chart)
import csv
from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "processed"
FIGURES_DIR = REPO_ROOT / "figures"

BUSINESS_LABELS = ["Transit/Access", "Content", "Enterprise"]
STRUCTURAL_LABELS = ["Customer-serving", "Peering edge", "Stub"]


def task4():
    relationships_file = DATA_DIR / "relationships_clean.csv"
    classifications_file = DATA_DIR / "as2types_20210401_clean.csv"
    degrees_file = DATA_DIR / "as_degrees.csv"

    relationship_asns = set()
    with open(relationships_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            relationship_asns.update((int(row["as1"]), int(row["as2"])))

    classifications = {}
    with open(classifications_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            asn = int(row["asn"])
            category = row["type"]
            if category not in BUSINESS_LABELS:
                raise ValueError(f"Unexpected business label {category!r} for AS{asn}")
            classifications[asn] = category

    structural_roles = {}
    with open(degrees_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            asn = int(row["asn"])
            if asn not in relationship_asns:
                continue
            customer_degree = int(row["d_c"])
            peer_degree = int(row["d_p"])
            if customer_degree > 0:
                role = "Customer-serving"
            elif peer_degree > 0:
                role = "Peering edge"
            else:
                role = "Stub"
            structural_roles[asn] = role

    missing_degrees = relationship_asns - structural_roles.keys()
    if missing_degrees:
        raise ValueError(f"Missing degree data for {len(missing_degrees)} relationship ASes")

    classified_asns = set(classifications)
    matched_asns = relationship_asns & classified_asns
    excluded_classifications = classified_asns - relationship_asns
    excluded_relationships = relationship_asns - classified_asns

    contingency = {
        business_label: {role: 0 for role in STRUCTURAL_LABELS}
        for business_label in BUSINESS_LABELS
    }
    for asn in matched_asns:
        contingency[classifications[asn]][structural_roles[asn]] += 1

    print(f"Matched sample size: {len(matched_asns):,}")
    print(f"Excluded 2021-classified ASes absent from the 2024 graph: "
          f"{len(excluded_classifications):,}")
    print(f"Excluded 2024-graph ASes without a 2021 classification: "
          f"{len(excluded_relationships):,}")
    print("\nContingency table (AS counts):")
    print(f"{'Business label':<18}" + "".join(f"{role:>20}" for role in STRUCTURAL_LABELS))
    for business_label in BUSINESS_LABELS:
        print(f"{business_label:<18}" + "".join(
            f"{contingency[business_label][role]:>20,}" for role in STRUCTURAL_LABELS
        ))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    table = ax.table(
        cellText=[
            [business_label]
            + [f"{contingency[business_label][role]:,}" for role in STRUCTURAL_LABELS]
            for business_label in BUSINESS_LABELS
        ],
        colLabels=["2021 business label"] + STRUCTURAL_LABELS,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)
    ax.set_title(
        f"2021 business labels × 2024 structural roles (matched N = {len(matched_asns):,})",
        pad=18,
    )
    fig.text(
        0.5,
        0.06,
        f"Excluded: {len(excluded_classifications):,} classified ASes absent from graph; "
        f"{len(excluded_relationships):,} graph ASes unclassified in 2021",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    output_path = FIGURES_DIR / "task4_contingency_table.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved contingency table: {output_path}")


if __name__ == "__main__":
    task4()