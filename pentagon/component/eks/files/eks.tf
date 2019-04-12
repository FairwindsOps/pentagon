

locals {
  cluster_name          = "{{ cluster_name }}"

  tags                  = {
    environment         = "{{ environment }}"
  }

  availability_zones    = {{ availability_zones }}

  aws_iam_roles         = [
    {
      role_arn  = "${aws_iam_role.role_kube_engineer.arn}"
      username  = "KubernetesEngineer"
      group     = "engineers"
    },
    {
      role_arn  = "${aws_iam_role.role_kube_developer.arn}"
      username  = "KubernetesDeveloper"
      group     = "developers"
    }
  ]
}



resource "aws_key_pair" "eks-key" {
  key_name = ""
  public_key = "${file("${path.root}/../config/private/admin_rsa.pub")}"
}

module "eks-cluster" {
  source                                = "terraform-aws-modules/eks/aws"
  cluster_name                          = "${local.cluster_name}"
  cluster_version                       = "{{ kubernetes_version }}"
  config_output_path                    = "./"
  write_kubeconfig                      = true
  manage_aws_auth                       = true
  write_aws_auth_config                 = false
  cluster_create_security_group         = true
  worker_create_security_group          = true
  vpc_id                                = "{{ vpc_id }}"
  subnets                               = ["${module.vpc.private_subnets}"]
  worker_group_count                    = 3
  worker_additional_security_group_ids  = ["${aws_security_group.all_worker_mgmt.id}"]
  map_accounts                          = [""]
  map_accounts_count                    = 0
  tags                                  = "${local.tags}"
  map_roles                             = "${local.aws_iam_roles}"
  map_roles_count                       = 2
  workers_additional_policies           = ["${aws_iam_policy.external-dns.arn}"]
  workers_additional_policies_count     = 1


  worker_groups = [
{% for az in availability_zones -%}
    {
      name                  = "nodes-{{ az }}"
      instance_type         = "{{ worker_node_type }}"
      autoscaling_enabled   = true
      protect_from_scale_in = true
      asg_min_size          = {{ ig_min_size if ig_min_size else node_count }}
      asg_max_size          = {{ ig_max_size if ig_max_size else node_count }}
      subnets               = "${module.vpc.private_subnets[0]}"
      key_name              = "${aws_key_pair.eks-key.key_name}"
    },
{% endfor -%}
  ]
}
