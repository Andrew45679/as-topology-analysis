import csv
import os
import matplotlib.pyplot as plt
from data_prep import read_as_rel2, drop_conflicts, build_graphs, read_as_org

rows, counts = read_as_rel2("data/raw/20241101.as-rel2.txt")
clean_rows, dropped = drop_conflicts(rows)
customers, providers, peers, neighbors = build_graphs(clean_rows)
as_names, org_counts = read_as_org("data/raw/20251001.as-org2info.txt")


# Customer cone: the AS itself plus every AS reachable by going
# provider -> customer. `cone` is the visited set, so each AS is
# added only once (no double-counting) and a cycle can't loop forever.
def customer_cone(start):
    cone = {start}
    to_visit = [start]
    while to_visit:
        asn = to_visit.pop()
        for cust in customers.get(asn, set()):
            if cust not in cone:
                cone.add(cust)
                to_visit.append(cust)
    return cone


# Cone size for every AS. ASes with no customers have a cone of just themselves.
cone_size = {}
for asn in neighbors:
    if asn in customers:
        cone_size[asn] = len(customer_cone(asn))
    else:
        cone_size[asn] = 1


# Sort ASes from largest to smallest
by_cone = sorted(neighbors, key=lambda a: cone_size[a], reverse=True)
by_degree = sorted(neighbors, key=lambda a: len(neighbors[a]), reverse=True)


# Table 1: top 15 customer cones
os.makedirs("figures", exist_ok=True)
with open("figures/task5_table_top15_cones.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["rank", "asn", "organization", "global_degree",
                     "customer_degree", "cone_size", "degree_rank"])
    for rank, asn in enumerate(by_cone[:15], 1):
        row = [rank, asn, as_names.get(asn, "unknown"),
               len(neighbors[asn]), len(customers.get(asn, set())),
               cone_size[asn], by_degree.index(asn) + 1]
        writer.writerow(row)
        print(row)

# For the comparison: where the top 10 by degree rank by cone size
print("\nTop 10 by degree:")
for asn in by_degree[:10]:
    print(asn, as_names.get(asn, "unknown"), "degree", len(neighbors[asn]),
          "cone", cone_size[asn], "cone rank", by_cone.index(asn) + 1)


# Graph 6: cone size of the top 100 ASes, largest first
plt.figure(figsize=(9, 5))
plt.plot(range(1, 101), [cone_size[a] for a in by_cone[:100]], marker=".")
plt.yscale("log")
plt.xlabel("Rank by customer-cone size")
plt.ylabel("Customer-cone size (number of ASes, log scale)")
plt.title(f"Graph 6: Top 100 customer cones (N = {len(neighbors):,} ASes, Nov 2024)")
plt.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("figures/graph6_top100_cones.png", dpi=200)
plt.close()
