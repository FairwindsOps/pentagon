
resource "aws_key_pair" "eks-key" {
  key_name = ""
  public_key = "${file("${path.root}/../config/private/admin_rsa.pub")}"
}

module "eks-cluster" {
  source                                = "terraform-aws-modules/eks/aws"
  cluster_name                          = "${local.cluster_name}"
  cluster_version                       = "1.11"
  config_output_path                    = "./"
  write_kubeconfig                      = false
  manage_aws_auth                       = true
  write_aws_auth_config                 = false
  cluster_create_security_group         = true
  worker_create_security_group          = true
  vpc_id                                = "${module.vpc.vpc_id}"
  subnets                               = ["${module.vpc.private_subnets}"]
  worker_group_count                    = 3
  worker_additional_security_group_ids  = ["${aws_security_group.all_worker_mgmt.id}"]
  map_accounts                          = [""]
  map_accounts_count                    = 0
  tags                                  = "${local.tags}"
  map_roles                             = "${local.aws_iam_roles}"
  map_roles_count                       = 3
  workers_additional_policies           = ["${aws_iam_policy.external-dns.arn}"]
  workers_additional_policies_count     = 1


  worker_groups = [
    {
      name                  = "k8s-nodes-${local.availability_zones[0]}"
      instance_type         = "m4.large"
      autoscaling_enabled   = true
      protect_from_scale_in = true
      asg_min_size          = 1
      asg_max_size          = 3
      subnets               = "${module.vpc.private_subnets[0]}"
      key_name              = "${aws_key_pair.eks-key.key_name}"
    },
    {
      name                  = "k8s-nodes-${local.availability_zones[1]}"
      instance_type         = "m4.large"
      autoscaling_enabled   = true
      protect_from_scale_in = true
      asg_min_size          = 1
      asg_max_size          = 3
      subnets               = "${module.vpc.private_subnets[1]}"
      key_name              = "${aws_key_pair.eks-key.key_name}"
    },
    {
      name                  = "k8s-nodes-${local.availability_zones[2]}"
      instance_type         = "m4.large"
      autoscaling_enabled   = true
      protect_from_scale_in = true
      asg_min_size          = 1
      asg_max_size          = 3
      subnets               = "${module.vpc.private_subnets[2]}"
      key_name              = "${aws_key_pair.eks-key.key_name}"
    }
  ]
}
