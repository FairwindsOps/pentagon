export KUBE_AWS_ZONE="us-west-2a"
export KUBERNETES_PROVIDER="aws"
export KUBERNETES_SKIP_DOWNLOAD=1
# Re: KUBE_AWS_INSTANCE_PREFIX, see: https://github.com/kubernetes/kubernetes/issues/24854
export KUBE_AWS_INSTANCE_PREFIX="production"
export AWS_S3_BUCKET="kubernetes-scripts-"$ORG_NAME

# Set these after something something
export VPC_ID="vpc-e221b886"

export SUBNET_ID="subnet-4a34813c"

export MASTER_RESERVED_IP=172.20.64.9

export AWS_SSH_KEY="/Users/justin/Documents/work/reactive/workspace/projects/micron/micron-infrastructure/config/private/production_kube_aws_rsa"

export KUBE_ENABLE_NODE_PUBLIC_IP="false"


export NON_MASQUERADE_CIDR="172.16.0.0/14"
export SERVICE_CLUSTER_IP_RANGE="172.16.0.0/16"
export DNS_SERVER_IP="172.16.0.10"
export MASTER_IP_RANGE="172.17.0.0/24"
export CLUSTER_IP_RANGE="172.18.0.0/16"
