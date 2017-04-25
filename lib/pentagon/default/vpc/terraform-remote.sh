#!/usr/bin/env  bash
set -x

export STATE_STORAGE=s3
export STATE_BUCKET=${KOPS_STATE_STORE}
# change for multiple VPCs:
export STATE_KEY=${INFRASTRUCTURE_BUCKET}/${DEFAULT_VPC_TAG}/tfstate
export STATE_REGION=${AWS_DEFAULT_REGION}

echo "configuring remote state ${STATE_STORAGE}://${STATE_BUCKET}/${STATE_KEY} in ${STATE_REGION}"

terraform remote config -backend="${STATE_STORAGE}"              \
                        -backend-config="bucket=${STATE_BUCKET}" \
                        -backend-config="key=${STATE_KEY}"       \
                        -backend-config="region=${STATE_REGION}"
