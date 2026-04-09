"""Shared test fixtures — bin systems, councils, and user-data builder."""

import json


# ---------------------------------------------------------------------------
# Bin system data pulled from DynamoDB bin_systems table.
# ---------------------------------------------------------------------------

no_bin_system = {
    "id": "56",
    "bins": [
        {
            "id": "56-no-bin-system-no-kerbside-collection",
            "type": "No Kerbside Collection",
            "appearance": "No Bin System",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": True,
            "extras": [],
        },
    ],
}

r_y_lg_fogo = {
    "id": "19",
    "bins": [
        {
            "id": "19-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "19-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
        {
            "id": "19-lime-green-food-and-garden-waste",
            "type": "Food and Garden Waste",
            "appearance": "Lime Green",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
    ],
}

r_y = {
    "id": "1",
    "bins": [
        {
            "id": "1-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "1-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
    ],
}

g_y = {
    "id": "7",
    "bins": [
        {
            "id": "7-green-garbage",
            "type": "Garbage",
            "appearance": "Green",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "7-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
    ],
}

g = {
    "id": "2",
    "bins": [
        {
            "id": "2-green-garbage",
            "type": "Garbage",
            "appearance": "Green",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": True,
            "extras": [],
        },
    ],
}

r_y_lg_go = {
    "id": "5",
    "bins": [
        {
            "id": "5-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "5-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
        {
            "id": "5-lime-green-garden-waste",
            "type": "Garden Waste",
            "appearance": "Lime Green",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
    ],
}

r_nogo_y = {
    "id": "4",
    "bins": [
        {
            "id": "4-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "4-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
    ],
}

r_y_p_lg_fogo = {
    "id": "60",
    "bins": [
        {
            "id": "60-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "60-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "60-purple-recycling",
            "type": "Recycling",
            "appearance": "Purple",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
        {
            "id": "60-lime-green-food-and-garden-waste",
            "type": "Food and Garden Waste",
            "appearance": "Lime Green",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
    ],
}

r_y_b_lg_fogo = {
    "id": "23",
    "bins": [
        {
            "id": "23-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "23-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
        {
            "id": "23-blue-recycling",
            "type": "Recycling",
            "appearance": "Blue",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "23-lime-green-garden-waste",
            "type": "Garden Waste",
            "appearance": "Lime Green",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
    ],
}

r_y_sp = {
    "id": "111",
    "bins": [
        {
            "id": "111-red-garbage",
            "type": "Garbage",
            "appearance": "Red",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "111-yellow-recycling",
            "type": "Recycling",
            "appearance": "Yellow",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": ["soft-plastics-orange-bag"],
        },
    ],
}

no_recycling_system = {
    "id": "87",
    "bins": [
        {
            "id": "87-green-garbage",
            "type": "Garbage",
            "appearance": "Green",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
        {
            "id": "87-maroon-food-and-garden-waste",
            "type": "Food and Garden Waste",
            "appearance": "Maroon",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": True,
            "acceptsGlass": False,
            "extras": [],
        },
    ],
}

bag_system = {
    "id": "80",
    "bins": [
        {
            "id": "80-byo-garbage",
            "type": "Garbage",
            "appearance": "BYO",
            "acceptsGarbage": True,
            "acceptsSoftPlastics": True,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
        {
            "id": "80-clear/red-recycling",
            "type": "Recycling",
            "appearance": "Clear/Red",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": True,
            "acceptsContainers": True,
            "acceptsFood": False,
            "acceptsGarden": False,
            "acceptsGlass": True,
            "extras": [],
        },
        {
            "id": "80-clear/green-food-waste",
            "type": "Food Waste",
            "appearance": "Clear/Green",
            "acceptsGarbage": False,
            "acceptsSoftPlastics": False,
            "acceptsCardboard": False,
            "acceptsContainers": False,
            "acceptsFood": True,
            "acceptsGarden": False,
            "acceptsGlass": False,
            "extras": [],
        },
    ],
}


# ---------------------------------------------------------------------------
# Council mappings — one real council per bin system.
# ---------------------------------------------------------------------------

COUNCILS = {
    "56": {"id": "298", "name": "Victoria Daly Regional Council"},
    "19": {"id": "99", "name": "City of Mount Gambier"},
    "1": {"id": "357", "name": "Inverell Shire Council"},
    "7": {"id": "207", "name": "Shire of Williams"},
    "2": {"id": "168", "name": "Shire of Westonia"},
    "5": {"id": "328", "name": "Upper Lachlan Shire Council"},
    "4": {"id": "467", "name": "Mount Alexander Shire Council"},
    "60": {"id": "440", "name": "Moira Shire Council"},
    "23": {"id": "344", "name": "Mosman Council"},
    "111": {"id": "464", "name": "Alpine Shire Council"},
    "87": {"id": "485", "mapId": "200", "name": "Hume City Council"},
    "80": {"id": "546", "mapId": "250", "name": "Mt Buller Mt Stirling Alpine Resort"},
}


# ---------------------------------------------------------------------------
# Helper to build user_data JSON for prompt_args.
# ---------------------------------------------------------------------------

def make_user_data(
    slug: str,
    bin_sys: dict,
    *,
    name: str | None = None,
    pod_configuration: str = "none",
    pod_bin_preferences: dict | None = None,
) -> str:
    """Build a serialised user_data dict for a given bin system.

    Keyword args:
        name: optional user name
        pod_configuration: "none" | "freestanding" | "in_drawer" | "under_sink"
        pod_bin_preferences: optional Pod bin preference mapping dict
    """
    data: dict = {
        "id": f"eval-user-{slug}",
        "email": f"eval-{slug}@test.com",
        "council": COUNCILS[bin_sys["id"]],
        "bin_system": bin_sys,
        "pod_configuration": pod_configuration,
        "points": 0,
    }
    if name is not None:
        data["name"] = name
    if pod_bin_preferences is not None:
        data["pod_bin_preferences"] = pod_bin_preferences
    return json.dumps(data)
