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

###
# Organization specific variables
###

variable "vpc_cidr" {
  default = "172.20"
}

variable "aws_vpc_name" {}
###
# VPC module specific variables
###

variable "az_count" {
  default = 3
}
variable "vpc_cidr_base" {}

variable "admin_subnet_parent_cidr" {}
variable "admin_subnet_cidrs" {
  default = {}
}

variable "public_subnet_parent_cidr" {}
variable "public_subnet_cidrs" {
  default = {}
}

variable "private_prod_subnet_parent_cidr" {}
variable "private_prod_subnet_cidrs" {
  default = {}
}

variable "private_working_subnet_parent_cidr" {}
variable "private_working_subnet_cidrs" {
  default = {}
}
