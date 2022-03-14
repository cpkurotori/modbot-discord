import requests
import yaml

with open("config.yaml") as config_file:
    config = yaml.load(config_file, yaml.SafeLoader)

application_id = config["discord"]["bot"]["application_id"]
guilds = config["discord"]["guilds"]
bot_token = config["discord"]["bot"]["token"]

create_command_body = {
    "name": "Mark as Violation",
    "type": 3,
    "default_permission": False,
}


headers = {"Authorization": f"Bot {bot_token}"}

for guild in guilds:
    guild_id = guild["id"]
    url = f"https://discord.com/api/v8/applications/{application_id}/guilds/{guild_id}/commands"
    resp = requests.post(url, headers=headers, json=create_command_body)
    print(
        f"request to create command complete method=POST url={url} status_code={resp.status_code}"
    )

    command_resp = resp.json()
    command_id = command_resp["id"]

    create_permissions_body = {
        "permissions": [
            {"id": allowed, "type": 1, "permission": True}
            for allowed in guild["allowed"]
        ]
    }

    url = f"https://discord.com/api/v8/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions"
    resp = requests.put(url, headers=headers, json=create_permissions_body)
    print(
        f"request to create permissions method=PUT url={url} status_code={resp.status_code}"
    )
