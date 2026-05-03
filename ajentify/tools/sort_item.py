def sort_item(classification, context):
    user_defined = context.get("user_defined", {})
    user_data_str = user_defined.get("user_data", "{}")
    user_data = json.loads(user_data_str)
    bin_system = user_data.get("bin_system", {})
    bins = bin_system.get("bins", [])

    category_to_flag = {
        "cardboard": "acceptsCardboard",
        "container": "acceptsContainers",
        "food": "acceptsFood",
        "garbage": "acceptsGarbage",
        "garden": "acceptsGarden",
        "glass": "acceptsGlass",
        "soft_plastic": "acceptsSoftPlastics",
    }

    flag = category_to_flag.get(classification.lower())
    if not flag:
        return {"error": "Unknown classification: " + str(classification)}

    for b in bins:
        if b.get(flag, False):
            result = {
                "bin_type": b.get("type"),
                "bin_appearance": b.get("appearance"),
                "classification": classification,
            }
            extras = b.get("extras", [])
            if extras:
                result["extras"] = extras
            return result

    return {
        "no_bin_found": True,
        "classification": classification,
        "message": "No kerbside bin accepts this material category"
    }
