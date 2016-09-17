// Sample main.tf

provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region = "${var.aws_region}"
}

module "vpc" {
  /*source = "git::ssh://git@github.com/reactiveops/terraform-vpc.git?ref=1.1.0"*/
  source = "./terraform-vpc"
  aws_vpc_name = "${var.aws_vpc_name}"
  aws_access_key = "${var.aws_access_key}"
  aws_secret_key = "${var.aws_secret_key}"
  aws_region = "${var.aws_region}"

  az_count =  "${var.az_count}"
  aws_azs = "${var.aws_azs}"

  /*network = "${var.vpc_cidr}"*/
  vpc_cidr_base = "${var.vpc_cidr_base}"

  nat_instance_enabled = "${var.nat_instance_enabled}"
  nat_gateway_enabled = "${var.nat_gateway_enabled}"

  /*nat_key_name = "${var.nat_key_name}"
  nat_instance_type = "${var.nat_instance_type}"*/

}
