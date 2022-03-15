import requests
import yaml
import sys

config_filepath = (len(sys.argv) > 1 and sys.argv[1]) or "config.yaml"

with open(config_filepath) as config_file:
    config = yaml.load(config_file, yaml.SafeLoader)

application_id = config["discord"]["bot"]["application_id"]
guilds = config["discord"]["guilds"]
bot_token = config["discord"]["bot"]["token"]

create_command_bodies = [
    {
        "name": "Mark as Violation",
        "type": 3,  # message command
        "default_permission": False,
    },
    {
        "name": "violation",
        "type": 1,  # slash command
        "default_permission": False,
        "description": "Choose a message to mark as violating a server rule",
        "options": [
            {
                "name": "message_id",
                "type": 3,  # string
                "description": "the message id (or message url) that is violating a server rule",
                "required": True,
            }
        ],
    },
]


headers = {"Authorization": f"Bot {bot_token}"}

for guild in guilds:
    guild_id = guild["id"]
    create_url = f"https://discord.com/api/v8/applications/{application_id}/guilds/{guild_id}/commands"
    for create_command_body in create_command_bodies:
        resp = requests.post(create_url, headers=headers, json=create_command_body)
        print(
            f"request to create command complete method=POST url={create_url} status_code={resp.status_code}"
        )

        command_resp = resp.json()

        print(command_resp)
        command_id = command_resp["id"]

        create_permissions_body = {
            "permissions": [
                {"id": allowed, "type": 1, "permission": True}
                for allowed in guild["allowed"]
            ]
        }

        permissions_url = f"https://discord.com/api/v8/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions"
        resp = requests.put(
            permissions_url, headers=headers, json=create_permissions_body
        )
        print(
            f"request to create permissions method=PUT url={permissions_url} status_code={resp.status_code}"
        )
