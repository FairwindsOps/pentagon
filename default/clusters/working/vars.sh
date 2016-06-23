export KUBE_AWS_ZONE="us-east-1b"
export KUBERNETES_PROVIDER="aws"
export KUBERNETES_SKIP_DOWNLOAD=1
# Re: KUBE_AWS_INSTANCE_PREFIX, see: https://github.com/kubernetes/kubernetes/issues/24854
export KUBE_AWS_INSTANCE_PREFIX="working"
export AWS_S3_BUCKET="kubernetes-scripts-"$ORG_NAME
export AWS_SSH_KEY="${INFRASTRUCTURE_REPO}/config/private/${KUBE_AWS_INSTANCE_PREFIX}_kube_aws_rsa"
export KUBE_ENABLE_NODE_PUBLIC_IP="false"

# After terraform apply, get the VPC ID, and subnet and set it here:
export VPC_ID="vpc-b1fd54d6"

# private_working_az1:
export SUBNET_ID="subnet-932571b9"
# The routing table associated with this subnet needs to be metadata tagged: KubernetesCluster : working

export MASTER_RESERVED_IP=172.20.96.9
