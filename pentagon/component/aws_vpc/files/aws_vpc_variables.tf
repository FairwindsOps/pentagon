variable "aws_region" {}
variable "aws_azs" {}

variable "aws_vpc_name" {}

variable "az_count" {}
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
