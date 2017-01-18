#!/usr/bin/env  bash
set -x

# @Todo - 

# change state-key to $module-name/$vpc-name/terraform.tfstate
# kops and terraform state, should be in the same s3_bucket
# loc: default/account/vars.sh


export STATE_STORAGE=s3
export STATE_BUCKET=${KOPS_STATE_STORE_BUCKET}
export STATE_KEY=${PROJECT_NAME}/${CLUSTER_NAME}/tfstate/
export STATE_REGION=${AWS_DEFAULT_REGION}

echo "configuring remote state ${STATE_STORAGE}://${STATE_BUCKET}/${STATE_KEY} in ${STATE_REGION}"

terraform remote config -backend="${STATE_STORAGE}"              \
                        -backend-config="bucket=${STATE_BUCKET}" \
                        -backend-config="key=${STATE_KEY}"       \
                        -backend-config="region=${STATE_REGION}"

