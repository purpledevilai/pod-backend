#!/usr/bin/env python3
"""
Analyze CouncilAndBinData to find concrete councils + postcodes for each
bin system configuration listed in bin_systems_analysis.md.

Output: a markdown table per configuration with example councils & postcodes
suitable for testing the app.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent

with open(DATA_DIR / "bin_systems.json") as f:
    bin_systems = json.load(f)
with open(DATA_DIR / "councils.json") as f:
    councils = json.load(f)
with open(DATA_DIR / "council_to_bin_systems.json") as f:
    council_to_bin_systems = json.load(f)
with open(DATA_DIR / "postal_code_to_councils.json") as f:
    postal_code_to_councils = json.load(f)


def classify_system(system: dict) -> str:
    """Classify a bin system into one of the high-level configurations."""
    bins = system["bins"]
    types = [b["type"] for b in bins]
    type_counter = Counter(types)
    n = len(bins)

    if n == 1 and types[0] == "No Kerbside Collection":
        return "No Kerbside Collection"
    if n == 1 and types[0] == "Garbage":
        return "Garbage only (1-bin)"
    if n == 2 and type_counter == Counter(["Garbage", "Recycling"]):
        return "Garbage + Recycling (2-bin)"
    if n == 3 and type_counter == Counter(["Garbage", "Recycling", "Food and Garden Waste"]):
        return "Garbage + Recycling + Food & Garden Waste (3-bin)"
    if n == 3 and type_counter == Counter(["Garbage", "Recycling", "Garden Waste"]):
        return "Garbage + Recycling + Garden Waste (3-bin)"
    if n == 4 and type_counter == Counter(["Garbage", "Recycling", "Recycling", "Food and Garden Waste"]):
        return "Garbage + 2x Recycling + Food & Garden Waste (4-bin)"
    if n == 4 and type_counter == Counter(["Garbage", "Recycling", "Recycling", "Garden Waste"]):
        return "Garbage + 2x Recycling + Garden Waste (4-bin)"
    return f"Other: {sorted(type_counter.items())} (n={n})"


postcodes_by_council = defaultdict(list)
for pc, council_ids in postal_code_to_councils.items():
    for cid in council_ids:
        postcodes_by_council[cid].append(pc)


def system_summary(system: dict) -> str:
    parts = []
    for b in system["bins"]:
        parts.append(f"{b['appearance']} {b['type']}")
    return " + ".join(parts)


def state_from_postcode(pc: str) -> str:
    if not pc or not pc.isdigit():
        return ""
    n = int(pc)
    if 1000 <= n <= 2599 or 2620 <= n <= 2899 or 2921 <= n <= 2999:
        return "NSW"
    if 200 <= n <= 299 or 2600 <= n <= 2618 or 2900 <= n <= 2920:
        return "ACT"
    if 3000 <= n <= 3999 or 8000 <= n <= 8999:
        return "VIC"
    if 4000 <= n <= 4999 or 9000 <= n <= 9999:
        return "QLD"
    if 5000 <= n <= 5799 or 5800 <= n <= 5999:
        return "SA"
    if 6000 <= n <= 6797 or 6800 <= n <= 6999:
        return "WA"
    if 7000 <= n <= 7999:
        return "TAS"
    if 800 <= n <= 999:
        return "NT"
    return ""


def appearance_signature(system: dict) -> str:
    """Type-Appearance signature ordered by type, used to group variants."""
    parts = sorted(f"{b['type']}:{b['appearance']}" for b in system["bins"])
    return " | ".join(parts)


buckets = defaultdict(lambda: defaultdict(list))

for cid, info in council_to_bin_systems.items():
    council_name = info["council_name"]
    default = next((s for s in info["bin_systems"] if s.get("is_default")), None)
    if default is None:
        continue
    full_system = bin_systems.get(default["id"])
    if full_system is None:
        continue
    config = classify_system(full_system)
    sig = appearance_signature(full_system)
    pcs = sorted(postcodes_by_council.get(cid, []))
    buckets[config][sig].append({
        "council_id": cid,
        "name": council_name,
        "system_id": default["id"],
        "summary": system_summary(full_system),
        "postcodes": pcs,
    })


CONFIGS_IN_ORDER = [
    "Garbage + Recycling (2-bin)",
    "Garbage + Recycling + Food & Garden Waste (3-bin)",
    "Garbage only (1-bin)",
    "Garbage + Recycling + Garden Waste (3-bin)",
    "No Kerbside Collection",
    "Garbage + 2x Recycling + Food & Garden Waste (4-bin)",
    "Garbage + 2x Recycling + Garden Waste (4-bin)",
]

print("# Bin Configuration Test Councils\n")
print("Each section below lists the actual council count, plus a handful of")
print("recommended example councils with at least one valid postcode you can")
print("type into the app to set the council.\n")

WELL_KNOWN_HINTS = {
    "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Hobart", "Darwin",
    "Canberra", "Newcastle", "Wollongong", "Geelong", "Gold Coast", "Sunshine Coast",
    "Mosman", "Manly", "Bondi", "Waverley", "Stonnington", "Yarra", "Port Phillip",
    "Boroondara", "Glen Eira", "Bayside", "Northern Beaches", "North Sydney",
    "Sutherland", "Parramatta", "Inner West", "Randwick", "Woollahra", "Ku-ring-gai",
    "Lane Cove", "Hunter's Hill", "Hobsons Bay", "Frankston", "Whittlesea",
    "Casey", "Kingston", "Monash", "Maribyrnong", "Merri-bek", "Moreland",
    "Cassowary", "Ipswich", "Logan", "Townsville", "Cairns", "Mackay",
    "Hume", "Banyule", "Manningham", "Whitehorse", "Knox",
    "Fremantle", "Stirling", "Subiaco", "Vincent",
    "Onkaparinga", "Salisbury", "Marion", "Charles Sturt", "Norwood",
    "Launceston", "Hobart", "Glenorchy",
}


def is_well_known(name: str) -> bool:
    return any(hint in name for hint in WELL_KNOWN_HINTS)


def pick_examples(items: list, n: int = 4) -> list:
    items_with_pc = [c for c in items if c["postcodes"]]
    well_known = [c for c in items_with_pc if is_well_known(c["name"])]
    others = [c for c in items_with_pc if not is_well_known(c["name"])]
    seen = set()
    picks = []
    for c in well_known + others:
        if c["council_id"] in seen:
            continue
        seen.add(c["council_id"])
        picks.append(c)
        if len(picks) >= n:
            break
    return picks


for config in CONFIGS_IN_ORDER:
    variants = buckets.get(config, {})
    total = sum(len(v) for v in variants.values())
    print(f"\n## {config}")
    print(f"_Total councils with this default: **{total}**_\n")
    if not variants:
        print("_No councils found._")
        continue

    sorted_variants = sorted(variants.items(), key=lambda kv: -len(kv[1]))
    for sig, items in sorted_variants:
        picks = pick_examples(items, n=4)
        if not picks:
            continue
        print(f"### Variant: `{picks[0]['summary']}`  ({len(items)} councils, system id `{picks[0]['system_id']}`)\n")
        print("| Council | Council ID | State | Example Postcode |")
        print("|---|---|---|---|")
        for c in picks:
            pc = c["postcodes"][0]
            print(f"| {c['name']} | {c['council_id']} | {state_from_postcode(pc)} | {pc} |")
        print()


print("\n## Other / Rare Configurations\n")
for config, variants in buckets.items():
    if config in CONFIGS_IN_ORDER:
        continue
    total = sum(len(v) for v in variants.values())
    print(f"\n### {config}")
    print(f"_{total} councils_\n")
    print("| Council | Council ID | State | Example Postcode | System |")
    print("|---|---|---|---|---|")
    for items in variants.values():
        for c in items:
            if not c["postcodes"]:
                continue
            pc = c["postcodes"][0]
            print(f"| {c['name']} | {c['council_id']} | {state_from_postcode(pc)} | {pc} | `{c['summary']}` |")
