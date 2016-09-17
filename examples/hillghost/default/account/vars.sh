export KOPS_STATE_STORE_BUCKET="hillghost-kops-state"
export KOPS_STATE_STORE=s3://${KOPS_STATE_STORE_BUCKET}

# if bucket does not exist:
# aws s3 mb s3://$KOPS_STATE_STORE_BUCKET
# aws s3api put-bucket-versioning --bucket s3://$KOPS_STATE_STORE_BUCKET --versioning-configuration Status=Enabled
