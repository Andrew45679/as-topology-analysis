# Internet AS Topology, Hierarchy, and Routing

ECE 478/578 — Fundamentals of Computer Networks, Project 2

Analysis of the Internet at the Autonomous System (AS) level using CAIDA measurement data. The project covers AS business classifications, provider–customer and peer–peer relationships, degree distributions, advertised IPv4 address space, customer cones, robustness to AS failures, and candidate Tier-1 ASes.

## Datasets

All files are provided on D2L and go in `data/raw/`. They are not committed to the repository.

| File | Snapshot | Contents |
|---|---|---|
| `20150801.as2types.txt` | Aug 2015 | AS business classification |
| `20210401.as2types.txt` | Apr 2021 | AS business classification |
| `20241101.as-rel2.txt` | Nov 2024 | Inferred AS relationships |
| `routeviews-rv2-20251110-1200.pfx2as.txt` | Nov 2025 | IPv4 prefix-to-origin-AS mappings |
| `20251001.as-org2info.txt` | Oct 2025 | AS-to-organization information |

CAIDA relationships and classifications are inferences from available observations, not exhaustive ground truth.

## Repository structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                  # input files from D2L (not committed)
│   └── processed/            # cleaned CSVs (big prefix file is parsed once)
├── src/
│   ├── data_prep.py          # all parsers, cleaning log, conflict policy, graph builder
│   ├── task1_classification.py
│   ├── task2_degrees.py
│   ├── task3_prefixes.py
│   ├── task4_roles.py
│   ├── task5_cones.py
│   ├── task6_robustness.py
│   └── task7_clique.py
├── test_prefix_union.py
└── figures/                  # all plots and table CSVs for the report
```

`data_prep.py` is the only shared file. It holds the cleaning rules and the conflict policy so every task uses identical data. Each task script imports from it and writes its own plots and tables to `figures/`.

## Setup

Requires Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Suggested dependencies: `pandas`, `numpy`, `matplotlib`, `pytest`.

Place the five data files in `data/raw/`.

## Running the analysis

Run the steps in this order, since later tasks read intermediate files from earlier ones.

```bash
# 1. Parse and clean all inputs (writes data/processed/ and the cleaning log)
python src/data_prep.py

# 2. Degrees (needed by tasks 4 and 7)
python src/task2_degrees.py

# 3. Remaining tasks (any order)
python src/task1_classification.py
python src/task3_prefixes.py
python src/task4_roles.py
python src/task5_cones.py
python src/task6_robustness.py
python src/task7_clique.py

# 4. Prefix-union test
pytest test_prefix_union.py
```

Tasks 1 and 3 do not depend on the relationship graph and can be run independently.

## Tasks and outputs

| Task | Description | Outputs |
|---|---|---|
| 1 | AS business classification and evolution (2015 vs. 2021) | Graph 1 |
| 2 | Relationships and degree distributions | Graphs 2, 3; top-10 degree table |
| 3 | Advertised IPv4 prefixes and address space | Graphs 4a, 4b; two example ASes |
| 4 | Business labels vs. structural roles | 3×3 contingency table; Graph 5 |
| 5 | Internet hierarchy and customer cones | Table 1 (top 15 cones); Graph 6 |
| 6 | Structural robustness under AS failures | Robustness plot (random vs. targeted) |
| 7 | Peering core and candidate Tier-1 ASes | Clique table |

## One-week sprint (two people)

Start date: Fri, Nov 13. **Plan B target: submit Fri, Nov 20.** The real deadline is Mon, Nov 24, so Nov 21-24 is backup time only. Check items off as you finish them.

**Work split (about 7 to 7.5 hours of coding each, plus an equal share of the report):**

| | P1 (graph track) | P2 (data track) |
|---|---|---|
| Parsing | `as-rel2` file, graph builder | `as2types` (both years), prefix file, org file |
| Tasks | 2, 4, 5, 7 | 1, 3, 6 |
| Report | Methodology (relationship data), interpretations for Tasks 2, 4, 5, 7, limitations | Methodology (classification, prefix, and org data), interpretations for Tasks 1, 3, 6, AI-use statement |

### Week 1: Build, analyze, and write up (Days 1-7)

Goal: finish all seven tasks, check the numbers, and submit the PDF report.

**Days 1-2 (Fri-Sat, Nov 13-14): Setup and data cleaning**

- [ ] Both (`README.md`, `requirements.txt`, `.gitignore`): Create the repo, add this README, `requirements.txt`, `.gitignore` (include `data/raw/`), and the folders.
- [ ] Both: Download the five files from D2L and open each one to check the headers and format.
- [ ] Both: Agree on file names for the cleaned CSVs, the random seed, and how to word denominators in the report.
- [ ] P1 (`src/data_prep.py`): Read `as-rel2`. Count the comment lines, bad rows, duplicates, and self-links.
- [ ] P1 (`src/data_prep.py`): Look for AS pairs with conflicting relationships, pick a rule for them, and write it down.
- [ ] P1 (`src/data_prep.py`): Save one clean relationship file and build the directed and undirected graphs.
- [ ] P2 (`src/data_prep.py`): Read both `as2types` files and count the comment lines, bad rows, and duplicates.
- [ ] P2 (`src/data_prep.py`): Read the prefix file (including prefixes with more than one origin AS) and count the same things.
- [ ] P2 (`src/data_prep.py`, `test_prefix_union.py`): Write the prefix-union function and its test (`10.0.0.0/16` + `10.0.1.0/24` = 65,536).
- [ ] P2 (`src/data_prep.py`): Read the org file. It has two sections with different columns.
- [ ] Both: Keep a log of every cleaning count. You will need these numbers for the methodology.
- [ ] Milestone (Day 2): clean relationship and prefix data are saved, and the prefix-union test passes. Fix this first if it fails.

**Days 2-4 (Sat-Mon, Nov 14-16): Main analysis**

- [ ] P1 (`src/task2_degrees.py`): Task 2: compute the four degrees for every AS and check that `d = d_c + d_p + d_r`.
- [ ] P1 (`src/task2_degrees.py`): Task 2: make Graph 2 (histograms), Graph 3 (CCDF), the summary stats, and the top-10 table.
- [ ] P1: Send `as_degrees.csv` to P2 by the end of Day 2.
- [ ] P1 (`src/task5_cones.py`): Task 5: find each AS's customer cone with BFS/DFS and a visited set. Only start from ASes that have customers.
- [ ] P1 (`src/task5_cones.py`): Task 5: make Table 1 (top 15 cones) and Graph 6, then compare degree rank to cone rank.
- [ ] P2 (`src/task1_classification.py`): Task 1: count ASes per category for 2015 and 2021, work out the percentages, and make Graph 1.
- [ ] P2 (`src/task3_prefixes.py`): Task 3: compute P and A for each AS and check that the total address space is at most 2^32.
- [ ] P2 (`src/task3_prefixes.py`): Task 3: make Graphs 4a and 4b and pick two example ASes (many prefixes, small address space).
- [ ] P2 (`src/task6_robustness.py`): Task 6: remove nodes at random (10+ seeded trials) and by highest degree at f = 0, 1, 2, 5, 10%.
- [ ] Both: Start writing each interpretation as soon as its numbers are checked, while they are fresh.
- [ ] Milestone (Day 4): Tasks 1, 2, 3, 5, and 6 are done and checked.

**Days 4-5 (Mon-Tue, Nov 16-17): Roles, Tier-1, and cross-checks**

These tasks use data from earlier tasks. Give the Task 4 join extra time.

- [ ] P1 (`src/task4_roles.py`): Task 4: label each AS (customer-serving, peering edge, or stub), join with the classification file, and make the 3x3 table. Report matched and unmatched counts.
- [ ] P1 (`src/task4_roles.py`): Task 4: make Graph 5 and look into two or three ASes with odd label combinations.
- [ ] P1 (`src/task7_clique.py`): Task 7: build the clique from the highest-degree ASes (use the top-50 fallback if needed) and make the table with organizations and link counts.
- [ ] P2 (`src/task6_robustness.py`): Task 6: finish the plot with min-max or standard deviation ranges.
- [ ] P2 (`src/data_prep.py`): Give P1 the clean classification file and help check the Task 4 join counts.
- [ ] P1: Write the interpretations for Tasks 2, 4, 5, and 7.
- [ ] P2: Write the interpretations for Tasks 1, 3, and 6.
- [ ] Both: Swap with your partner and double-check at least one task each.
- [ ] Milestone (Day 5): all seven tasks are done and double-checked.

**Days 5-7 (Tue-Thu, Nov 17-19): Finish the report and get it ready**

This is where teams most often run out of time. Do not leave it for the last night.

- [ ] Both (`src/task*.py`, `figures/`): Remake your own graphs with final labels, units, and denominators.
- [ ] P1: Write the methodology for the relationship data: snapshot date, cleaning counts, conflict rule, and the two graph versions.
- [ ] P2: Write the methodology for the classification, prefix, and org data: snapshot dates, cleaning counts, how multi-origin prefixes are handled, and denominators.
- [ ] P1: Write the limitations (data is inferred, snapshot dates range from 2015 to 2025).
- [ ] P2: Write the AI-use statement describing how you used AI for code, plots, and debugging.
- [ ] Both: Put your own graphs and tables in the report with captions. Number the tables carefully, since Tasks 5 and 7 are both called "Table 1" in the assignment.
- [ ] Both (Day 6): Read each other's sections, recheck the numbers against your code output, and make the writing sound like one voice.
- [ ] Both (Day 6): Final check: every graph and table is there, every percentage names its denominator, and facts are kept separate from your guesses.
- [ ] Both (Day 7, Thu Nov 19): Fix anything left, export the PDF, and make sure it opens.
- [ ] Milestone (Day 7): PDF report is finished and ready to submit.

**Submit (Fri, Nov 20)**

- [ ] Both: Do a last read of the PDF, then submit it. This is the Plan B target.
- [ ] Backup (Sat-Mon, Nov 21-24): Only use this time if something slipped. The real deadline is Mon, Nov 24.

If you fall behind, protect the written interpretations first, since most of the grade depends on them. Skip plot polish before skipping analysis.

## References

1. CAIDA, AS Classification Dataset: https://www.caida.org/catalog/datasets/as-classification/
2. CAIDA, AS Relationships Dataset: https://www.caida.org/catalog/datasets/as-relationships/
3. CAIDA, RouteViews Prefix-to-AS Mappings: https://www.caida.org/catalog/datasets/routeviews-prefix2as/
4. CAIDA, AS Organizations: https://www.caida.org/catalog/datasets/as-organizations/
5. M. Luckie et al., "AS Relationships, Customer Cones, and Validation," ACM Internet Measurement Conference, 2013.
