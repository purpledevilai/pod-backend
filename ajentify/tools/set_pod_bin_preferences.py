def set_pod_bin_preferences(context, pod_bin_preferences):

    user_defined = context.get("user_defined", {})
    auth_token = user_defined.get("user_auth_token")
    pod_api_url = user_defined.get("pod_api_url")

    prefs = {k: v for k, v in pod_bin_preferences.items() if v}

    response = requests.post(
        f"{pod_api_url}/set-pod-bin-preferences",
        headers={
            "Authorization": auth_token,
            "Content-Type": "application/json",
        },
        json={"pod_bin_preferences": prefs},
    )

    if response.status_code != 200:
        return f"Failed to save Pod bin preferences: {response.text}"

    return f"Pod bin preferences saved successfully"
