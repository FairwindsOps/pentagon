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
