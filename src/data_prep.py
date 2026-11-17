

# Count the comment lines, bad rows, duplicates, and self-links.
def read_as_rel2 (file_path):
    counts = {
        "comment_lines": 0,
        "bad_rows": 0,
        "duplicates": 0,
        "self_links": 0
    }

    rows = []
    seen = set()

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            a = b = rel = None
            try:
                parts = line.split("|")
                a, b, rel = int(parts[0]), int(parts[1]), int(parts[2])
            except (ValueError, IndexError):
                pass

            if line.startswith("#"):
                counts["comment_lines"] += 1
            elif a is None or rel not in (-1, 0):
                counts["bad_rows"] += 1
            elif a == b:
                counts["self_links"] += 1
            elif (a, b, rel) in seen:
                counts["duplicates"] += 1
            else:
                seen.add((a, b, rel))
                rows.append((a, b, rel))

    return rows, counts

def drop_conflicts (rows):
    pair_rows = {}
    for a, b, rel in rows:
        if rel == 0:
            a, b = min(a, b), max(a, b)     
        pair = frozenset((a, b))
        if pair not in pair_rows:
            pair_rows[pair] = set()
        pair_rows[pair].add((a, b, rel))

    clean_rows = []
    dropped = 0

    for pairs in pair_rows.values():
        if len(pairs) == 1:              
            clean_rows.append(next(iter(pairs)))
        else:                                
            dropped += 1
    return clean_rows, dropped


def build_graphs(clean_rows):
    customers = {}
    providers = {}
    peers = {}
    neighbors = {}

    for a, b, rel in clean_rows:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
        if rel == -1:
            customers.setdefault(a, set()).add(b)
            providers.setdefault(b, set()).add(a)
        else:
            peers.setdefault(a, set()).add(b)
            peers.setdefault(b, set()).add(a)

    return customers, providers, peers, neighbors

