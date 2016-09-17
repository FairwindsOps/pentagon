variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}

variable "aws_vpc_name" {
  default = "vpc"
}

variable "aws_azs" {
  description = "comma separated string of availability zones in order of precedence"
  default = "us-east-1a, us-east-1d, us-east-1e, us-east-1c"

}

variable "az_count" {
  description = "number of active availability zones in VPC"
  default = "3"
}

variable "vpc_cidr_base" {
  default = "10.20"
}

variable "vpc_instance_tenancy" {
  default = "default"
}

variable "vpc_enable_dns_support" {
  default = "true"
}

variable "vpc_enable_dns_hostnames" {
  default = "true"
}

variable "vpc_enable_classiclink" {
  default = "false"
}

variable "admin_subnet_parent_cidr" {
  description = "parent CIDR for the administrative subnets"
  default = ".0.0/19"
}

variable "admin_subnet_cidrs" {
  description = "CIDRs for the adminsitrative subnets"
  default = {
    zone0 = ".0.0/21"
    zone1 = ".8.0/21"
    zone2 = ".16.0/21"
    zone3 = ".24.0/21"
  }
}

variable "public_subnet_parent_cidr" {
  description = "parent CIDR for the public subnets"
  default = ".32.0/19"
}

variable "public_subnet_cidrs" {
  description = "CIDRs for the public subnets"
  default = {
    zone0 = ".32.0/21"
    zone1 = ".40.0/21"
    zone2 = ".48.0/21"
    zone3 = ".56.0/21"
  }
}

variable "private_prod_subnet_parent_cidr" {
  description = "parent CIDR for the private production subnets"
  default = ".64.0/19"
}

variable "private_prod_subnet_cidrs" {
  description = "CIDRs for the private production subnets"
  default = {
    zone0 = ".64.0/21"
    zone1 = ".72.0/21"
    zone2 = ".80.0/21"
    zone3 = ".88.0/21"
  }
}

variable "private_working_subnet_parent_cidr" {
  description = "parent CIDR for the private working subnets"
  default = ".96.0/19"
}

variable "private_working_subnet_cidrs" {
  description = "CIDRs for the private working subnets"
  default = {
    zone0 = ".96.0/21"
    zone1 = ".104.0/21"
    zone2 = ".112.0/21"
    zone3 = ".120.0/21"
  }
}

variable "aws_nat_ami" {
  default = {
    us-east-1 = "ami-4868ab25"
    us-west-1 = "ami-004b0f60"
    us-west-2 = "ami-a275b1c2"
    ap-northeast-1 = "ami-2443b745"
    ap-southeast-1 = "ami-a79b49c4"
    ap-southeast-2 = "ami-53371f30"
    eu-west-1 = "ami-a8dd45db"
    sa-east-1 = "ami-9336bcff"
  }
}

variable "nat_instance_enabled" {
  description = "set to 1 to create nat ec2 instances for private subnets"
  default = 0
}

variable "nat_gateway_enabled" {
  description = "set to 1 to create nat gateway instances for private subnets"
  default = 0
}

variable "nat_instance_type" {
  default = "t2.micro"
}

variable "nat_key_name" {
  default = ""
}
