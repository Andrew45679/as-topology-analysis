import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from data_prep import read_as_rel2, drop_conflicts, build_graphs

rows, counts = read_as_rel2("data/raw/20241101.as-rel2.txt")
clean_rows, dropped = drop_conflicts(rows)
customers, providers, peers, neighbors = build_graphs(clean_rows)


degrees = []
violations = 0

for asn in neighbors:
    d = len(neighbors[asn])
    d_c = len(customers.get(asn, set()))
    d_p = len(peers.get(asn, set()))
    d_r = len(providers.get(asn, set()))

    if d != d_c + d_p + d_r:
        violations += 1

    degrees.append((asn, d, d_c, d_p, d_r))


with open("data/processed/as_degrees.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["asn", "d", "d_c", "d_p", "d_r"])
    writer.writerows(degrees)


print(f"ASes: {len(degrees)}  identity violations: {violations}")
print("cleaning counts:", counts, " conflicting pairs dropped:", dropped)


# Graph 2: four degree histograms with the assignment's bins
# 0, 1, 2-5, 6-100, 101-500, 501-1000, >1000.
# Degrees are whole numbers, so the edges below give exactly those bins:
# [0,1) = 0, [1,2) = 1, [2,6) = 2-5, ..., [1001, inf) = >1000.
# The last edge is infinity so the >1000 bin catches every large AS.
edges = [0, 1, 2, 6, 101, 501, 1001, np.inf]
labels = ["0", "1", "2–5", "6–100", "101–500", "501–1000", ">1000"]

# Count how many ASes fall in each bin, for each of the four degree types.
# The columns of each degrees row are (asn, d, d_c, d_p, d_r).
d_counts, _ = np.histogram([row[1] for row in degrees], bins=edges)
dc_counts, _ = np.histogram([row[2] for row in degrees], bins=edges)
dp_counts, _ = np.histogram([row[3] for row in degrees], bins=edges)
dr_counts, _ = np.histogram([row[4] for row in degrees], bins=edges)

# every AS must land in exactly one bin of each histogram
assert d_counts.sum() == dc_counts.sum() == dp_counts.sum() == dr_counts.sum() == len(degrees)

print("Global degree (d)    ", dict(zip(labels, d_counts.tolist())))
print("Customer degree (d_c)", dict(zip(labels, dc_counts.tolist())))
print("Peer degree (d_p)    ", dict(zip(labels, dp_counts.tolist())))
print("Provider degree (d_r)", dict(zip(labels, dr_counts.tolist())))

os.makedirs("figures", exist_ok=True)
fig = plt.figure(figsize=(12, 9))

# The y-axis is log scale because the bins range from tens of thousands of
# ASes down to a handful. The bottom is 0.5 so a bin with 1 AS still shows.
# A count of 0 can't be drawn on a log axis, so empty bins get a "0" label.

# Histogram 1: global degree (d)
plt.subplot(2, 2, 1)
bars = plt.bar(labels, d_counts, edgecolor="black")
plt.bar_label(bars, labels=[f"{c:,}" for c in d_counts], fontsize=8)
plt.yscale("log")
plt.ylim(0.5, d_counts.max() * 3)
plt.text("0", 0.6, "0", ha="center", va="bottom", fontsize=8)  # empty bin: every AS has at least 1 link
plt.title("Global degree (d)")
plt.xlabel("Degree bin")
plt.ylabel("Number of ASes (log scale)")

# Histogram 2: customer degree (d_c)
plt.subplot(2, 2, 2)
bars = plt.bar(labels, dc_counts, edgecolor="black")
plt.bar_label(bars, labels=[f"{c:,}" for c in dc_counts], fontsize=8)
plt.yscale("log")
plt.ylim(0.5, dc_counts.max() * 3)
plt.title("Customer degree (d_c)")
plt.xlabel("Degree bin")
plt.ylabel("Number of ASes (log scale)")

# Histogram 3: peer degree (d_p)
plt.subplot(2, 2, 3)
bars = plt.bar(labels, dp_counts, edgecolor="black")
plt.bar_label(bars, labels=[f"{c:,}" for c in dp_counts], fontsize=8)
plt.yscale("log")
plt.ylim(0.5, dp_counts.max() * 3)
plt.title("Peer degree (d_p)")
plt.xlabel("Degree bin")
plt.ylabel("Number of ASes (log scale)")

# Histogram 4: provider degree (d_r)
plt.subplot(2, 2, 4)
bars = plt.bar(labels, dr_counts, edgecolor="black")
plt.bar_label(bars, labels=[f"{c:,}" for c in dr_counts], fontsize=8)
plt.yscale("log")
plt.ylim(0.5, dr_counts.max() * 3)
plt.text("501–1000", 0.6, "0", ha="center", va="bottom", fontsize=8)  # empty bin
plt.text(">1000", 0.6, "0", ha="center", va="bottom", fontsize=8)     # empty bin
plt.title("Provider degree (d_r)")
plt.xlabel("Degree bin")
plt.ylabel("Number of ASes (log scale)")

fig.suptitle(f"Graph 2: AS degree histograms (N = {len(degrees):,} ASes, CAIDA as-rel2, Nov 2024)")
fig.tight_layout()
fig.savefig("figures/graph2_degree_histograms.png", dpi=200)
plt.close(fig)

# Summary numbers for global degree
# (denominator: all ASes in the 2024 relationship file)
d_all = np.array([row[1] for row in degrees])
print(f"Global degree: mean {d_all.mean():.2f}  median {np.median(d_all):.0f}  "
      f"95th pct {np.percentile(d_all, 95):.0f}  max {d_all.max()}")


# Graph 3: CCDF of global degree, Pr(D >= k), log-log axes, k >= 1
ks = np.sort(np.unique(d_all))
ccdf = [(d_all >= k).mean() for k in ks]

plt.figure(figsize=(7, 5))
plt.loglog(ks, ccdf, marker=".", linestyle="none")
plt.xlabel("Global degree k (number of neighboring ASes)")
plt.ylabel("Pr(D ≥ k)")
plt.title(f"Graph 3: CCDF of global AS degree (N = {len(d_all):,} ASes, Nov 2024)")
plt.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("figures/graph3_degree_ccdf.png", dpi=200)
plt.close()


# Top-10 ASes by global degree, with all four degrees
top10 = sorted(degrees, key=lambda r: r[1], reverse=True)[:10]

with open("figures/table_top10_degree.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["rank", "asn", "d", "d_c", "d_p", "d_r"])
    for i, row in enumerate(top10, 1):
        writer.writerow([i, *row])
        print(i, *row)

