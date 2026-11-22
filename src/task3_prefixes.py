#                               TASK 3
# 1) For each origin AS i, compute P_i, the number of distinct advertised IPv4 prefixes
# 2) For each origin AS i, compute A_i, the number of unique IPv4 addresses covered
#   NOTE: if a prefix is mapped to more than one origin AS, associate the prefix with each listed origin
# 3) Plot the distributions of P_i and A_i over the observed origin ASes. Choose readable bins (logarithmic bins are acceptable)
from pathlib import Path
from data_prep import prefix_union_address_count
import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "processed"
FIGURES_DIR = REPO_ROOT / "figures"


def task3():
    prefixes_per_asn = {}

    filePath = DATA_DIR / "pfx2as_20251110_clean.csv"
    with open(filePath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("prefix"):
                continue
            prefix, prefix_length, asn_line = line.split(",")[0], line.split(",")[1], line.split(",")[2]
            asns = asn_line.split("_")
            for asn in asns:
                asn = int(asn)
                prefixes_per_asn.setdefault(asn, set()).add(f"{prefix}/{prefix_length}")

    P_i = {}
    A_i = {}

    for asn, prefixes in prefixes_per_asn.items():
        P_i[asn] = len(prefixes)
        A_i[asn] = prefix_union_address_count(prefixes)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    def plot_log_distribution(values, title, x_label, output_name):
        minimum = min(values)
        maximum = max(values)

        if minimum == maximum:
            bins = np.array([minimum * 0.5, maximum, maximum * 1.5])
        else:
            bins = np.geomspace(minimum, maximum * 1.01, 50)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(values, bins=bins, edgecolor="black", alpha=0.75)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(x_label)
        ax.set_ylabel("Number of origin ASes")
        ax.set_title(title)
        ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / output_name, dpi=200, bbox_inches="tight")
        plt.close(fig)

    plot_log_distribution(
        list(P_i.values()),
        "Graph 4a: Distribution of Advertised IPv4 Prefixes per Origin AS",
        "P_i: distinct advertised IPv4 prefixes",
        "graph4a_prefix_distribution.png",
    )
    plot_log_distribution(
        list(A_i.values()),
        "Graph 4b: Distribution of IPv4 Address Space per Origin AS",
        "A_i: unique IPv4 addresses covered",
        "graph4b_address_distribution.png",
    )

if __name__ == "__main__":
    task3()