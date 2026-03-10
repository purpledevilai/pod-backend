# Bin Systems Analysis

## Overview

- **543** total councils
- **67** unique bin systems
- **29** unique (type, appearance) combinations across all systems
- **6** distinct bin types: Garbage, Recycling, Garden Waste, Food and Garden Waste, Food Waste, No Kerbside Collection

## Uniqueness

- **Appearance is always unique** within a bin system — no system has two bins with the same appearance.
- **Type is not always unique** — 13 out of 67 systems have duplicate types (mostly split Recycling).
- **(Type, Appearance) is always unique** within a bin system.

## Default Bin System Configurations (Most to Least Common)

| Configuration | Councils | % |
|---|---|---|
| Garbage + Recycling (2-bin) | 166 | 30.6% |
| Garbage + Recycling + Food & Garden Waste (3-bin) | 158 | 29.1% |
| Garbage only (1-bin) | 90 | 16.6% |
| Garbage + Recycling + Garden Waste (3-bin) | 75 | 13.8% |
| No Kerbside Collection | 28 | 5.2% |
| Garbage + 2x Recycling + Food & Garden Waste (4-bin) | 14 | 2.6% |
| Garbage + 2x Recycling + Garden Waste (4-bin) | 7 | 1.3% |
| Other rare configs | 5 | 0.9% |

The classic **3-bin system** (Garbage + Recycling + green/organic waste) covers **42.9%** of councils (233 total).

## Split Recycling Systems

**23 councils (4.2%)** have a default bin system with duplicate Recycling types.

### How the recycling is split

The split always comes down to 3 fields: **Cardboard**, **Containers**, and **Glass**.

**Variant A** — Yellow/Blue or Yellow/Green (systems 17, 23, 26, 33, 46, 96):

| | Bin 1 | Bin 2 |
|---|---|---|
| Cardboard | - | YES |
| Containers | YES | - |
| Glass | YES | - |

**Variant B** — Yellow/Purple (systems 60, 70, 93, 94, 100, 107):

| | Bin 1 | Bin 2 |
|---|---|---|
| Cardboard | YES | - |
| Containers | YES | - |
| Glass | - | YES |

### Split recycling with or without a green bin

Of the 12 split-recycling bin systems:

- **8 are 4-bin systems** (include a green/organic bin) — systems 17, 23, 26, 33, 60, 70, 100, 107
- **4 are 3-bin systems** (no green bin) — systems 46, 93, 94, 96

### Councils with split recycling

| System | Councils |
|---|---|
| 17 (4-bin) | Mid-Western Regional Council |
| 23 (4-bin) | Hunter's Hill, Ku-ring-gai, Lane Cove, Mosman, Northern Beaches, Waverley |
| 26 (4-bin) | Shire of Denmark |
| 33 (4-bin) | Armidale Regional, Liverpool Plains Shire |
| 46 (3-bin) | Northern Beaches Council *(non-default)* |
| 60 (4-bin) | Frankston City, Hobsons Bay City, Macedon Ranges Shire, Merri-bek City, Moyne Shire, Surf Coast Shire, Warrnambool City, Yarra City |
| 70 (4-bin) | City of Whittlesea |
| 93 (3-bin) | Yarra City Council *(non-default)* |
| 94 (3-bin) | Yarra City, Frankston City *(non-default)* |
| 96 (3-bin) | Ku-ring-gai Council *(non-default)* |
| 100 (4-bin) | Colac Otway Shire, Horsham Rural City |
| 107 (4-bin) | Falls Creek Alpine Resort |

## Outlier: System 103 (Duplicate Garbage)

System 103 (Cassowary Coast Regional Council) is the only system with a duplicate **Garbage** type. The two bins are fully complementary:

| | Red | Green |
|---|---|---|
| Cardboard | - | YES |
| Containers | - | YES |
| Food | YES | - |
| Garbage | YES | - |
| Garden | YES | - |
| Glass | - | YES |
| Soft Plastics | YES | - |

The Green bin accepts recyclable materials, suggesting it may be better classified as "Recycling" rather than "Garbage".

## Appearance Patterns & Deviations from the "Standard"

The assumed standard pattern is: **Red = Garbage**, **Yellow = Recycling**, **Green/Lime Green = Garden waste**.

In practice, this pattern is far from universal — especially for Garbage.

### Garbage Appearance (default systems only)

| Appearance | Councils | % | Standard? |
|---|---|---|---|
| Red | 315 | 61.6% | Yes |
| Green | 183 | 35.8% | No |
| Blue | 11 | 2.2% | No |
| Purple | 1 | 0.2% | No |
| Yellow | 1 | 0.2% | No |

Over a third of councils use a **Green garbage bin** instead of Red. This is concentrated in WA shires, remote/rural QLD, SA, and TAS councils. Blue garbage bins appear in a handful of SA councils (e.g. Adelaide Hills, Alexandrina, City of Unley, City of Victor Harbor).

### Recycling Appearance (default systems only)

| Appearance | Councils | % | Standard? |
|---|---|---|---|
| Yellow | 402 | 91.4% | Yes |
| Blue | 15 | 3.4% | No |
| Purple | 11 | 2.5% | No |
| Green | 7 | 1.6% | No |
| Black Crate (no lid) | 2 | 0.5% | No |
| Black Crate (with lid) | 2 | 0.5% | No |
| Maroon | 1 | 0.2% | No |

Recycling is far more consistent — **91.4%** use Yellow. Blue and Purple are the main alternatives, with Purple being tied to the split-recycling Victorian councils.

### Garden Waste Appearance (default systems only)

| Appearance | Councils | % | Standard? |
|---|---|---|---|
| Lime Green | 72 | 86.7% | Yes |
| Green | 11 | 13.3% | Yes |

All Garden Waste bins follow the expected Green/Lime Green pattern.

### Food and Garden Waste Appearance (default systems only)

| Appearance | Councils | % | Standard? |
|---|---|---|---|
| Green | 86 | 50.0% | Yes |
| Lime Green | 85 | 49.4% | Yes |
| Maroon | 1 | 0.6% | No |

Nearly a perfect 50/50 split between Green and Lime Green. Only **City of Casey** uses a Maroon bin for Food and Garden Waste.

### Deep Dive: Green Garbage Bin Systems

183 councils use a Green garbage bin. Here's how those systems break down:

#### System configurations

| Config | Systems | Councils | Notes |
|---|---|---|---|
| Green Garbage only (1-bin) | 2, 3 | 80 | No recycling or garden waste at all |
| Green Garbage + Yellow Recycling (2-bin) | 7, 67, 75 | 88 | Standard 2-bin but green instead of red |
| Green Garbage + Recycling + Lime Green organic (3-bin) | 9, 13, 39, 40 | 8 | Organic bin is always Lime Green |
| Green Garbage + 2x Recycling + Lime Green organic (4-bin) | 17, 70 | 2 | Split recycling variant |
| System 103 — Red + Green Garbage (2-bin, no recycling) | 103 | 1 | Outlier, see above |

#### Companion bin colours

When a Green garbage bin exists alongside other bins:

- **Recycling** is Yellow in 93.3% of cases (97 councils). Blue (5), Purple (1), and Maroon (1) are rare alternatives.
- **Garden / Food & Garden Waste** is always **Lime Green** (never plain Green) — the system naturally avoids having two Green bins in the same lineup.
- The 80 councils with only a Green garbage bin (systems 2, 3) have no companion bins at all.

### Key Takeaway

The "Red = Garbage" assumption only holds for ~62% of councils. Any logic or UI that maps colours to bin types needs to account for the fact that **Green can mean either Garbage or Garden Waste** depending on the council — reinforcing that appearance alone should not be used to infer bin type without the bin system context.
