#!/usr/bin/env bash

# Set Environment Variables:
# * CR_ENDPOINT (example: 000000000.dkr.ecr.us-east-2.amazonaws.com)
# * CR_REGISTRY (example: modbot-discord)
# * AWS_LAMBDA_FUNCTION_STAGE (example: modbot-stage)

set -e

img="${CR_ENDPOINT}/${CR_REGISTRY}:latest"
echo "Updating to: ${img}"
aws lambda update-function-code --function-name ${AWS_LAMBDA_FUNCTION_STAGE} --architectures arm64 --image-uri ${img}  > /dev/null

status="InProgress"
while [[ "${status}" != "Successful" ]]; do
    sleep 5
    status="$(aws lambda get-function --function-name ${AWS_LAMBDA_FUNCTION_STAGE} | jq '.Configuration.LastUpdateStatus' -r)"
    echo "Status: ${status}"
done
echo "Done."