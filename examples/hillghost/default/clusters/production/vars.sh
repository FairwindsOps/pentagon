export NAME=hillghost-prod.hillghost.com
export ZONES="us-west-2a,us-west-2b,us-west-2c"
export VPC_ID="vpc-62270a06"

# the public key to be installed for the admin user
# this should be set to be unique per cluster
export SSH_KEY_PATH="${HOME}/workspace/projects/kubernetes-demo/dev-infra/config/private/devkey.pub"
