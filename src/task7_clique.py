#                                       TASK 7
# Infer the list of candidate Tier 1 ASes by computing the largest clique (complete graph) in the AS topology graph.
# To compute the largest clique, follow this simple greedy heuristic:
# 1) Rank all the ASes according to their global degree and organize them to a descending order set R = {AS_1, AS_2, ...}, where degree(AS_i) > degree(AS_i+1)
# 2) Initialize the clique S = {AS_1}
# 3) If AS_2 is connected to AS_1, via any type of link, add it to S; S = {AS_1, AS_2}
# 4) If AS_3 is connected to AS_1 and AS_2, add it to S; S = {AS_1, AS_2, AS_3}
# 5) Terminate when you find the first AS that is not connected to all ASes in S
# 6) Table: Report the size of the T1 list that you were able to discover and also report the first 10 ASes that were added to S
#           - The table should contain the AS number, the AS organization, and the number of incident links
# NOTE: It's possible that you do not find 10 ASes that form a clique and the algorithm terminates within the first 2-3 iterations. In this case, eliminate
# the AS that is NOT connected to all previous ASes in the clique and see if the next AS on your ranked list of ASes, by considering up to the top 50 ASes.
import csv
from pathlib import Path

from data_prep import read_as_rel2, drop_conflicts, build_graphs, read_as_org


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "processed"
FIGURES_DIR = REPO_ROOT / "figures"


def greedy_clique(ranked_asns, neighbors, stop_on_failure=False):
    """Build a clique from the first AS in degree order."""
    clique = [ranked_asns[0]]
    for asn in ranked_asns[1:]:
        if all(asn in neighbors[current] for current in clique):
            clique.append(asn)
        elif stop_on_failure:
            break

    return clique


def find_candidate_tier1(ranked_asns, neighbors):
    """Run the primary pass, then skip failed candidates within the top 50."""
    primary = greedy_clique(ranked_asns, neighbors, stop_on_failure=True)
    if len(primary) >= 10:
        return primary

    return greedy_clique(ranked_asns[:50], neighbors)


def task7():
    rows, cleaning_counts = read_as_rel2(
        str(REPO_ROOT / "data" / "raw" / "20241101.as-rel2.txt")
    )
    clean_rows, dropped_conflicts = drop_conflicts(rows)
    _, _, _, neighbors = build_graphs(clean_rows)

    ranked_asns = sorted(
        neighbors,
        key=lambda asn: (-len(neighbors[asn]), asn),
    )
    clique = find_candidate_tier1(ranked_asns, neighbors)

    org_path = REPO_ROOT / "data" / "raw" / "20251001.as-org2info1.txt"
    if not org_path.exists():
        org_path = REPO_ROOT / "data" / "raw" / "20251001.as-org2info.txt"
    as_names, org_counts = read_as_org(str(org_path))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / "task7_table_candidate_tier1.csv"
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "asn", "organization", "incident_links"])
        for rank, asn in enumerate(clique[:10], 1):
            writer.writerow([
                rank,
                asn,
                as_names.get(asn, "unknown"),
                len(neighbors[asn]),
            ])

    print(f"Candidate Tier-1 clique size: {len(clique)}")
    print("cleaning counts:", cleaning_counts,
          "conflicting pairs dropped:", dropped_conflicts)
    print("organization counts:", org_counts)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    task7()