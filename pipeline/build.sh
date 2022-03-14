#!/usr/bin/env bash

# Set Environment Variables:
# * CR_ENDPOINT (example: 000000000.dkr.ecr.us-east-2.amazonaws.com)
# * CR_REGISTRY (example: modbot-discord)

set -e

# uncomment the next line if you need to login
# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin ${CR_ENDPOINT}
docker build -t ${CR_REGISTRY} ..
docker tag modbot-discord:latest ${CR_ENDPOINT}/${CR_REGISTRY}:latest
docker push  ${CR_ENDPOINT}/${CR_REGISTRY}:latest