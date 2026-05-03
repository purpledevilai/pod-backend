def classify(item):
    table = {
        "cereal_box": "Yellow",
        "cereal box": "Yellow",
        "cardboard": "Yellow",
        "soft_plastic_liner": "Red",
        "soft plastic liner": "Red",
        "soft plastic": "Red",
        "plastic bottle": "Yellow",
        "water bottle": "Yellow",
        "metal cap": "Yellow",
        "glass bottle": "Yellow",
        "wine bottle": "Yellow",
        "banana peel": "Lime Green",
        "food scraps": "Lime Green",
        "broken mug": "Red",
        "garbage": "Red",
        "tree branch": None,
        "tree branches": None,
    }
    key = (item or "").strip().lower()
    if key in table:
        return {"bin_color": table[key]}
    return {"bin_color": "Yellow"}
