# VPC Setup

Verify:
* `default/vpc/terraform.tfvars` is configured properly
* $KOPS_STATE_STORE is set in `default/account/vars.sh`
* $AWS_DEFAULT_REGION is set in `config/private/vars`

Run:
* `bash terraform-remote.sh`
* `make plan`
* `make apply`
