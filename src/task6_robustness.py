import random
import matplotlib.pyplot as plt
from data_prep import read_as_rel2, drop_conflicts, build_graphs

# Load the 2024 AS graph
rows, counts = read_as_rel2("data/raw/20241101.as-rel2.txt")
clean_rows, dropped = drop_conflicts(rows)
customers, providers, peers, neighbors = build_graphs(clean_rows)

all_ases = list(neighbors)
total_ases = len(all_ases)

# The removal fractions from the assignment: 0%, 1%, 2%, 5%, 10%
fractions = [0, 0.01, 0.02, 0.05, 0.10]


# Work out R(f) after some ASes have been removed.
# R(f) = (remaining ASes that still have at least one link)
#        / (all remaining ASes)
def survival_ratio(removed):
    remaining_count = 0
    still_linked_count = 0

    for asn in all_ases:
        # Skip ASes that were removed
        if asn in removed:
            continue

        remaining_count += 1

        # Check if this AS still has at least one neighbor that was not removed
        has_link = False
        for neighbor in neighbors[asn]:
            if neighbor not in removed:
                has_link = True
                break

        if has_link:
            still_linked_count += 1

    return still_linked_count / remaining_count


# For targeted removal, sort the ASes from highest degree to lowest.
# This is done once, before anything is removed.
def get_degree(asn):
    return len(neighbors[asn])

ases_by_degree = sorted(all_ases, key=get_degree, reverse=True)


# Lists to hold the results for each fraction
targeted_results = []
random_average = []
random_lowest = []
random_highest = []

for f in fractions:
    # How many ASes to remove for this fraction
    number_to_remove = round(f * total_ases)

    # Targeted removal: remove the highest-degree ASes
    removed = set(ases_by_degree[:number_to_remove])
    targeted_results.append(survival_ratio(removed))

    # Random removal: do 10 trials, each with its own seed (0 to 9)
    trial_results = []
    for seed in range(10):
        random.seed(seed)
        removed = set(random.sample(all_ases, number_to_remove))
        trial_results.append(survival_ratio(removed))

    # Save the average, lowest, and highest result of the 10 trials
    random_average.append(sum(trial_results) / len(trial_results))
    random_lowest.append(min(trial_results))
    random_highest.append(max(trial_results))

    print("f =", f,
          "| removed:", number_to_remove,
          "| targeted R:", round(targeted_results[-1], 4),
          "| random R average:", round(random_average[-1], 4),
          "| min:", round(random_lowest[-1], 4),
          "| max:", round(random_highest[-1], 4))


# Graph 7: R(f) for both strategies
percent_removed = [f * 100 for f in fractions]

plt.figure(figsize=(8, 5))
plt.plot(percent_removed, targeted_results, marker="s", label="Targeted (highest degree first)")
plt.plot(percent_removed, random_average, marker="o", label="Random (average of 10 trials)")
plt.fill_between(percent_removed, random_lowest, random_highest, alpha=0.3,
                 label="Random min-max range")
plt.xlabel("ASes removed, f (%)")
plt.ylabel("R(f): fraction of remaining ASes with at least one link")
plt.title(f"Graph 7: Robustness under AS removal (N = {total_ases:,} ASes, Nov 2024)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/graph7_robustness.png", dpi=200)
plt.close()
