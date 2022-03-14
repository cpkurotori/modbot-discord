# modbot

`modbot` is a Discord bot built to facilitate easier moderation in your server. This implementation is specifically backed by the Function as a Service (FaaS), AWS Lambda.

## Usage

### Reporting message as a violation

**Via Message Command**

Currently, message commands only works on Desktop
1. Hover over message you want to report as a violation

<img src='imgs/message_options.png' alt='message options' width=350>

2. Click `...` to bring up more options and go to `App` and click `Mark as Violation`

<img src='imgs/message_command.png' alt='message command' width=350>

_Note: Please ignore the double command. You should only have one options unless you install a staging app._

3. Fill out the explanation of the violation and submit

<img src='imgs/violation_explanation.png' alt='violation explanation' width=350>

4. The bot will delete the message in the channel

<img src='imgs/deleted_message.png' alt='message deleted' width=350>

5. The bot will also DM the user with a notification that their message has been deleted

<img src='imgs/notification_message.png' alt='message deleted' width=350>




### Notes
- If you want to use the bot in a private channel, you must add the bot to the channel
    - Right click the channel and click `Channel Settings`
    - Go to `Permissions`
    - Add your bot user and/or your bot role

Adding to your own server
---

## Setup

Prerequisites:
- python3
- docker
- discord account
- discord server

### AWS
#### Required Infrastrucure:
- AWS Elastic Container Registry (and repository)
- AWS API Gateway
- AWS Lambda

#### Steps
1. Create AWS Elastic Container Registry repository
1. Build the image and push to AWS ECR (see [Build](#build))
1. Create AWS Lambda function
    1. Select `Container image`
    1. Under `Container image URI` find the image you pushed to ECR
    1. Architecture: `arm64`
1. Add trigger (expand `Function overview`)
    1. Select `API Gateway`
    1. `REST API`
    1. Security: `Open`
    1. Click `Add`
1. Create Discord Bot
    1. https://discord.com/developers/applications
    1. `New Application`
    1. Give it a name and `Create`
    1. `Bot` > `Add Bot`
    1. You can uncheck `Public Bot` if you don't want anyone else to use your application
    1. Enable `Message Content Intent`
1. Install Bot
    1. Go to generated link and add to your server
    1. Go to `Bot` and click `Reset token` and save this value for later (this value is a secret so keep it safe)
    1. Go to `General Infomation` and save your `Public Key` and `Application Id` for later
    1. Go to `https://discord.com/api/oauth2/authorize?client_id=<YOUR APPLICATION ID>&permissions=11264&scope=bot%20applications.commands` and install on your server (don't forget to replace `<YOUR APPLICATION ID>`)
1. Register the commands on your server
    1. Create your config file and save in same folder as `register_commands.py`
        ```yaml
        discord:
        bot:
            token: YOUR_BOT_TOKEN
            application_id: YOUR_BOTS_APPLICATION_ID
        guilds:
        - id: GUILD_ID
            allowed:
            - ROLE_ID_ALLOWED_TO_MODERATE
            - IT_CAN_BE_MULTIPLE
            - EACH_ROLE_ID_ON_NEW_LINE
        ```
    1. Run the following
        ```bash
        python3 -m pip install pyyaml requests
        python3 register_commands.py
        ```
1. Set bot Environment variables
    1. Go to your bot on AWS Lambda
    1. `Configuration` > `Environment Variable`
        - AUTHORIZED_GUILDS: comma separated list of server/guild ids
        - DISCORD_BOT_PUBLIC_KEY: public key from your Discord Bot information page (step 6)
        - DISCORD_BOT_TOKEN: private token from your Dicord Bot information page (step 6)
1. Add the URL for your function to your bot
    1. Go to your bot on AWS Lambda
    1. Go to `Configuration` > `Triggers`
    1. Copy the URL for your trigger
    1. Go to your bot's configuration on Discord
    1. Go to `General Information`
    1. Past the URL into `Interaction Endpoint URL` and click `Save Changes`


## Build
The build should be done when you are setting up or anytime the code changes and you
want to deploy the new version.


1. Login to your docker registry:   
    **AWS**: 
    
    `aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGION_URI}`
1. Build the image and push:
    ```bash
    docker build -t modbot-discord .
    docker tag modbot-discord:latest ${REGISTRY}:latest
    docker push ${REGISTRY}:latest
    ```

## Deploy Image (AWS)
This should be done anytime you push a new build

1. Go to your bot's AWS Lambda function
1. Go to `Image`
1. Click `Deploy new image`
1. Select the latest build
1. Click `Save`
1. Wait for the status overlay bar to turn green and indicate that the update is complete

    <img src='imgs/updating_function.png' width=500 alt='updating function'>

    <img src='imgs/update_complete.png' width=500 alt='update complete'>