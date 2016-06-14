export KUBE_AWS_ZONE="us-west-2a"
export KUBERNETES_PROVIDER="aws"
export KUBERNETES_SKIP_DOWNLOAD=1
# Re: KUBE_AWS_INSTANCE_PREFIX, see: https://github.com/kubernetes/kubernetes/issues/24854
export KUBE_AWS_INSTANCE_PREFIX="working"
export AWS_S3_BUCKET="kubernetes-scripts-"$ORG_NAME
