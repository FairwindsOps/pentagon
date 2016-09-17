variable "aws_vpc_id" {
  default = "vpc-62270a06"
}

/*Pick 1 of the the NAT Gateways*/
variable "aws_nat_gateway_id" {
  default = "nat-0cd618e1171d9e087"
}

variable "nodes_root_block_device_vol_size" {
  default = 100
}

variable "master_root_block_device_vol_size" {
  default = 100
}

variable "vpc_public_az1_id" {
  default = "subnet-e3c2aa95"
}
variable "vpc_public_az2_id" {
  default = "subnet-ab287bcf"
}
variable "vpc_public_az3_id" {
  default = "subnet-81e85dd9"
}

variable "route53_name_zone_id" {
  default = "Z2TQO6PXZ7B48Y"
}
