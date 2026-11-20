import csv
import ipaddress


# Read the AS relationship file and keep only the usable rows.
# Returns the kept rows as (as1, as2, rel) and a dictionary of counts
# for the lines that were skipped.
#   rel = -1 means as1 is the provider of as2
#   rel =  0 means as1 and as2 are peers
def read_as_rel2(file_path):
    # Tallies of the lines we skip, for the methodology section
    counts = {
        "comment_lines": 0,
        "bad_rows": 0,
        "duplicates": 0,
        "self_links": 0
    }

    # The rows we keep
    rows = []
    # Rows already kept, used to spot exact duplicates
    seen = set()

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Try to read the first three fields as numbers.
            # If the line is broken, a stays None so we can catch it below.
            a = b = rel = None
            try:
                parts = line.split("|")
                a, b, rel = int(parts[0]), int(parts[1]), int(parts[2])
            except (ValueError, IndexError):
                pass

            # Each line goes into exactly one bucket, checked in this order
            if line.startswith("#"):
                # A note in the file, not data
                counts["comment_lines"] += 1
            elif a is None or rel not in (-1, 0):
                # Couldn't read it, or the relationship is not -1 or 0
                counts["bad_rows"] += 1
            elif a == b:
                # An AS linked to itself
                counts["self_links"] += 1
            elif (a, b, rel) in seen:
                # An exact repeat of an earlier line
                counts["duplicates"] += 1
            else:
                # A good row: keep it
                seen.add((a, b, rel))
                rows.append((a, b, rel))

    return rows, counts


# Make sure each AS pair has only one relationship.
# A pair with more than one different relationship is a conflict, and the
# way this function deals with conflicts is to drop all conflicting rows.
# This is a conservative approach, but it ensures that the resulting graph
# is consistent.
# Returns the clean rows and the number of pairs that were dropped.
def drop_conflicts(rows):
    # Maps a pair of ASes to the set of different rows seen for that pair
    pair_rows = {}

    for a, b, rel in rows:
        # For peers, the order doesn't matter, so put the smaller AS first.
        # This way (24, 293, 0) and (293, 24, 0) count as the same row.
        if rel == 0:
            a, b = min(a, b), max(a, b)

        # A frozenset ignores order, so {24, 293} and {293, 24} are the same pair
        pair = frozenset((a, b))

        if pair not in pair_rows:
            pair_rows[pair] = set()
        pair_rows[pair].add((a, b, rel))

    clean_rows = []
    dropped = 0

    for pairs in pair_rows.values():
        if len(pairs) == 1:
            # Only one answer for this pair: keep it
            clean_rows.append(next(iter(pairs)))
        else:
            # More than one answer for this pair: drop it
            dropped += 1
    return clean_rows, dropped


# Build the graphs from the clean rows. Each one is a dictionary that maps an
# AS to a set of ASes it is connected to.
#   customers = provider -> its customers   (directed, used for customer cones)
#   providers = customer -> its providers
#   peers     = AS -> its peers
#   neighbors = AS -> every AS it is linked to (undirected, used for degree)
# Also saves the clean rows to a CSV file.
def build_graphs(clean_rows):
    customers = {}
    providers = {}
    peers = {}
    neighbors = {}

    for a, b, rel in clean_rows:
        # Every link goes in neighbors, in both directions.
        # setdefault makes an empty set the first time we see an AS.
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)

        if rel == -1:
            # a is the provider of b
            customers.setdefault(a, set()).add(b)
            providers.setdefault(b, set()).add(a)
        else:
            # Peers: the link goes both ways
            peers.setdefault(a, set()).add(b)
            peers.setdefault(b, set()).add(a)

    # Save the clean rows so other files can read them without cleaning again
    with open("data/processed/relationships_clean.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["as1", "as2", "rel"])
        writer.writerows(clean_rows)

    return customers, providers, peers, neighbors


# Read the AS-to-organization file and return a dictionary from AS number
# to organization name, plus a dictionary of counts.
# The file has two kinds of data lines, which we tell apart by column count:
#   5 columns = an organization: org_id|changed|org_name|country|source
#   6 columns = an AS: aut|changed|aut_name|org_id|opaque_id|source
def read_as_org(file_path):
    # org_id -> organization name
    org_names = {}
    # AS number -> org_id
    as_to_org = {}
    counts = {
        "comment_lines": 0,
        "bad_rows": 0,
        # ASes whose org_id has no organization name
        "no_org_name": 0
    }
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                counts["comment_lines"] += 1
                continue

            parts = line.strip().split("|")

            if len(parts) == 5:
                # Organization line: remember the name for this org_id
                org_id, date_changed, org_name, country, source = parts
                org_names[org_id] = org_name
            elif len(parts) == 6:
                # AS line: remember which org_id this AS belongs to
                asn, date_changed, aut_name, org_id, opaque_id, source = parts
                as_to_org[int(asn)] = org_id
            else:
                counts["bad_rows"] += 1

    # Join the two: for each AS, use its org_id to look up the organization name
    as_names = {}
    for asn, org_id in as_to_org.items():
        if org_id in org_names:
            as_names[asn] = org_names[org_id]
        else:
            counts["no_org_name"] += 1

    return as_names, counts


# Read the AS business classification files.
# Returns good rows and a dictionary of counts for the lines that were skipped.
#   Format: as|source|type
def read_as2types(file_path):
    counts = {
        "comment_lines": 0,
        "bad_rows": 0,
        "duplicates": 0
    }

    rows = []
    seen = set()

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                counts["comment_lines"] += 1
                continue

            parts = line.split("|")
            if len(parts) != 3:
                counts["bad_rows"] += 1
                continue

            try:
                as_id = int(parts[0])
            except ValueError:
                counts["bad_rows"] += 1
                continue

            src_name, category = parts[1].strip(), parts[2].strip()
            if as_id < 1 or as_id > 4294967294 or not src_name or not category:
                counts["bad_rows"] += 1
                continue

            if (as_id, src_name, category) in seen:
                counts["duplicates"] += 1
            else:
                seen.add((as_id, src_name, category))
                rows.append((as_id, src_name, category))

    return rows, counts


# Read the prefix-to-AS file.
# The dataset is used for IPv4 only.
# If a prefix has more than one origin AS, associate the prefix with each listed 
# origin for per-AS results, and count it only once when forming global unions.
# Returns good rows and a dictionary of counts for the lines that were skipped.
#   Format: IP_prefix   prefix_length   set_of_AS_numbers
#   Ex.:    16.14.207.0	24	20115
#           16.14.224.0	22	7843_20115
def read_pfx2as(file_path):
    counts = {
        "comment_lines": 0,
        "bad_rows": 0,
        "duplicates": 0
    }

    rows = []
    seen = set()

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                counts["comment_lines"] += 1
                continue
            if not line:
                counts["bad_rows"] += 1
                continue

            parts = line.split("\t")
            if len(parts) != 3:
                counts["bad_rows"] += 1
                continue

            pfx, length_text, origin_text = parts
            try:
                pfx_length = int(length_text)
                network = ipaddress.ip_network(f"{pfx}/{pfx_length}", strict=False)
            except (ValueError, ipaddress.AddressValueError, ipaddress.NetmaskValueError):
                counts["bad_rows"] += 1
                continue

            if network.version != 4 or not 0 <= pfx_length <= 32:
                counts["bad_rows"] += 1
                continue

            origin_parts = origin_text.replace(",", "_").split("_")
            try:
                origins = tuple(sorted(set(int(origin) for origin in origin_parts)))
            except ValueError:
                counts["bad_rows"] += 1
                continue

            if not origins or any(origin < 1 or origin > 4294967294 for origin in origins):
                counts["bad_rows"] += 1
                continue

            canonical_row = (str(network), pfx_length, origins)
            if canonical_row in seen:
                counts["duplicates"] += 1
            else:
                seen.add(canonical_row)
                rows.append(canonical_row)

    return rows, counts

# Return the number of unique IPv4 addresses covered by prefixes.
def prefix_union_address_count(prefixes):
    networks = []
    for prefix in prefixes:
        network = ipaddress.ip_network(prefix, strict=False)
        if network.version != 4:
            raise ValueError("prefix_union_address_count supports IPv4 only")
        networks.append(network)

    return sum(network.num_addresses for network in ipaddress.collapse_addresses(networks))