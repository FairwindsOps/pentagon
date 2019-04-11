module "vpc" {
  source                = "terraform-aws-modules/vpc/aws"
  version               = "1.14.0"
  name                  = "kubernetes-vpc"
  cidr                  = "172.21.0.0/16"
  azs                   = ["${local.availability_zones[0]}", "${local.availability_zones[1]}", "${local.availability_zones[2]}"]
  private_subnets       = ["172.21.0.0/22", "172.21.4.0/22", "172.21.8.0/22"]
  public_subnets        = ["172.21.12.0/22", "172.21.16.0/22", "172.21.20.0/22"]
  enable_nat_gateway    = true
  single_nat_gateway    = true
  tags                  = "${merge(local.tags, map("kubernetes.io/cluster/${local.cluster_name}", "shared"))}"
  enable_dns_hostnames  = true
}

resource "aws_security_group" "all_worker_mgmt" {
  name_prefix = "eks_worker_management"
  vpc_id      = "${module.vpc.vpc_id}"

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = [
      "172.21.0.0/16"
    ]
  }
}
