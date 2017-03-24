# INFRASTRUCTURE_BUCKET is the s3 bucket that will store terraform and kops state files
# export INFRASTRUCTURE_BUCKET="shareddev-infrastructure"
export INFRASTRUCTURE_BUCKET="<PLACEHOLDER>"

# Example DEFAULT_VPC_TAG : "20170131"
export DEFAULT_VPC_TAG="<PLACEHOLDER>"

# kops
export KOPS_STATE_STORE_BUCKET=$INFRASTRUCTURE_BUCKET
export KOPS_STATE_STORE="s3://${KOPS_STATE_STORE_BUCKET}"
