def set_user_name(context, name):

    user_defined = context.get("user_defined", {})
    auth_token = user_defined.get("user_auth_token")
    pod_api_url = user_defined.get("pod_api_url")

    response = requests.post(
        f"{pod_api_url}/set-user-name",
        headers={
            "Authorization": auth_token,
            "Content-Type": "application/json",
        },
        json={"name": name},
    )

    if response.status_code != 200:
        return f"Failed to save name: {response.text}"

    return f"Name saved successfully as {name}"
