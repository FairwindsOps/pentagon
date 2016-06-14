export KUBE_AWS_ZONE="us-west-2a"
export KUBERNETES_PROVIDER="aws"
export KUBERNETES_SKIP_DOWNLOAD=1
# Re: KUBE_AWS_INSTANCE_PREFIX, see: https://github.com/kubernetes/kubernetes/issues/24854
export KUBE_AWS_INSTANCE_PREFIX="production"
export AWS_S3_BUCKET="kubernetes-scripts-"$ORG_NAME

# Set these after creating the first cluster
export VPC_ID="vpc-664ddf02"
export SUBNET_ID="subnet-4f7cd439"
export MASTER_INTERNAL_IP=172.20.0.10
