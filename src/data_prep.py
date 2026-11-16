

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

    for line in open(file_path):
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

def find_as_pairs (rows):
    pass