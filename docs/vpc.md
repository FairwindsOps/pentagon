# VPC Setup

Create `terraform.tfvars` based on the example provided.

You also need to properly configure your terraform-remote state for both the VPC and the kops state-- they will be stored in the same s3 bucket. Check the envvars referenced in terraform-remote.sh.

* $KOPS_STATE_STORE should be set in `default/account/vars.sh`
* $AWS_DEFAULT_REGION should be set in `config/private/vars`

Then run:
`make plan`
`make apply`
