###
# AWS account specific variables
###

variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {
  default = "us-east-1"
}
variable "aws_azs" {
  default = "us-east-1a, us-east-1c, us-east-1d, us-east-1e"
}

variable "aws_inventory_path" {
  default = "$INFRASTRUCTURE_REPO/plugins/inventory"
}

###
# Organization specific variables
###

variable "vpc_cidr" {
  default = "10.10"
}

variable "aws_vpc_name" {}
###
# VPC module specific variables
###

variable "az_count" {
  default = 3
}
variable "vpc_cidr_base" {}
