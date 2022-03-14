#!/usr/bin/env bash

# Set Environment Variables:
# * CR_ENDPOINT (example: 000000000.dkr.ecr.us-east-2.amazonaws.com)
# * CR_REGISTRY (example: modbot-discord)
# * AWS_LAMBDA_FUNCTION_PROD: (example: modbot-prod)

set -e

img="${CR_ENDPOINT}/${CR_REGISTRY}:latest"
docker pull $img

prod_img="${CR_ENDPOINT}/${CR_REGISTRY}:prod"
docker tag "${img}" "${prod_img}"
docker push "${prod_img}"

aws lambda update-function-code --function-name ${AWS_LAMBDA_FUNCTION_PROD} --architectures arm64 --image-uri ${prod_img}  > /dev/null

status="InProgress"
while [[ "${status}" != "Successful" ]]; do
    sleep 5
    status="$(aws lambda get-function --function-name ${AWS_LAMBDA_FUNCTION_PROD} | jq '.Configuration.LastUpdateStatus' -r)"
    echo "Status: ${status}"
done
echo "Done."