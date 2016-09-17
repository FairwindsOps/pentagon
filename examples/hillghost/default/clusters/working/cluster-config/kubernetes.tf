provider "aws" {
  region = "us-west-2"
}

resource "aws_autoscaling_group" "master-us-west-2a-masters-kops-dev2-hillghost-com" {
  name = "master-us-west-2a.masters.kops-dev2.hillghost.com"
  launch_configuration = "${aws_launch_configuration.master-us-west-2a-masters-kops-dev2-hillghost-com.id}"
  max_size = 1
  min_size = 1
  vpc_zone_identifier = ["${aws_subnet.us-west-2a-kops-dev2-hillghost-com.id}"]
  load_balancers = ["${aws_elb.master-elb-hillghost-kops-dev2-hillghost-com.name}"]
  tag = {
    key = "KubernetesCluster"
    value = "kops-dev2.hillghost.com"
    propagate_at_launch = true
  }
  tag = {
    key = "Name"
    value = "master-us-west-2a.masters.kops-dev2.hillghost.com"
    propagate_at_launch = true
  }
  tag = {
    key = "k8s.io/dns/internal"
    value = "api.internal.kops-dev2.hillghost.com"
    propagate_at_launch = true
  }
  tag = {
    key = "k8s.io/dns/public"
    value = "api.kops-dev2.hillghost.com"
    propagate_at_launch = true
  }
  tag = {
    key = "k8s.io/role/master"
    value = "1"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_group" "nodes-kops-dev2-hillghost-com" {
  name = "nodes.kops-dev2.hillghost.com"
  launch_configuration = "${aws_launch_configuration.nodes-kops-dev2-hillghost-com.id}"
  max_size = 2
  min_size = 2
  vpc_zone_identifier = ["${aws_subnet.us-west-2a-kops-dev2-hillghost-com.id}", "${aws_subnet.us-west-2b-kops-dev2-hillghost-com.id}", "${aws_subnet.us-west-2c-kops-dev2-hillghost-com.id}"]
  tag = {
    key = "KubernetesCluster"
    value = "kops-dev2.hillghost.com"
    propagate_at_launch = true
  }
  tag = {
    key = "Name"
    value = "nodes.kops-dev2.hillghost.com"
    propagate_at_launch = true
  }
  tag = {
    key = "k8s.io/role/node"
    value = "1"
    propagate_at_launch = true
  }
}

resource "aws_ebs_volume" "us-west-2a-etcd-events-kops-dev2-hillghost-com" {
  availability_zone = "us-west-2a"
  size = 20
  type = "gp2"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "us-west-2a.etcd-events.kops-dev2.hillghost.com"
    "k8s.io/etcd/events" = "us-west-2a/us-west-2a"
    "k8s.io/role/master" = "1"
  }
}

resource "aws_ebs_volume" "us-west-2a-etcd-main-kops-dev2-hillghost-com" {
  availability_zone = "us-west-2a"
  size = 20
  type = "gp2"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "us-west-2a.etcd-main.kops-dev2.hillghost.com"
    "k8s.io/etcd/main" = "us-west-2a/us-west-2a"
    "k8s.io/role/master" = "1"
  }
}

resource "aws_iam_instance_profile" "masters-kops-dev2-hillghost-com" {
  name = "masters.kops-dev2.hillghost.com"
  roles = ["${aws_iam_role.masters-kops-dev2-hillghost-com.name}"]
}

resource "aws_iam_instance_profile" "nodes-kops-dev2-hillghost-com" {
  name = "nodes.kops-dev2.hillghost.com"
  roles = ["${aws_iam_role.nodes-kops-dev2-hillghost-com.name}"]
}

resource "aws_iam_role" "masters-kops-dev2-hillghost-com" {
  name = "masters.kops-dev2.hillghost.com"
  assume_role_policy = "${file("data/aws_iam_role_masters.kops-dev2.hillghost.com_policy")}"
}

resource "aws_iam_role" "nodes-kops-dev2-hillghost-com" {
  name = "nodes.kops-dev2.hillghost.com"
  assume_role_policy = "${file("data/aws_iam_role_nodes.kops-dev2.hillghost.com_policy")}"
}

resource "aws_iam_role_policy" "masters-kops-dev2-hillghost-com" {
  name = "masters.kops-dev2.hillghost.com"
  role = "${aws_iam_role.masters-kops-dev2-hillghost-com.name}"
  policy = "${file("data/aws_iam_role_policy_masters.kops-dev2.hillghost.com_policy")}"
}

resource "aws_iam_role_policy" "nodes-kops-dev2-hillghost-com" {
  name = "nodes.kops-dev2.hillghost.com"
  role = "${aws_iam_role.nodes-kops-dev2-hillghost-com.name}"
  policy = "${file("data/aws_iam_role_policy_nodes.kops-dev2.hillghost.com_policy")}"
}

/*resource "aws_internet_gateway" "kops-dev2-hillghost-com" {
  vpc_id = "${var.aws_vpc_id}"
  vpc_id = "${var.aws_vpc_id}"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "kops-dev2.hillghost.com"
  }
}*/

resource "aws_key_pair" "kubernetes-kops-dev2-hillghost-com-b9a1c2c419a63029501e849a8b56bad1" {
  key_name = "kubernetes.kops-dev2.hillghost.com-b9:a1:c2:c4:19:a6:30:29:50:1e:84:9a:8b:56:ba:d1"
  public_key = "${file("data/aws_key_pair_kubernetes.kops-dev2.hillghost.com-b9a1c2c419a63029501e849a8b56bad1_public_key")}"
}

resource "aws_launch_configuration" "master-us-west-2a-masters-kops-dev2-hillghost-com" {
  name_prefix = "master-us-west-2a.masters.kops-dev2.hillghost.com-"
  image_id = "ami-66884c06"
  instance_type = "m3.large"
  key_name = "${aws_key_pair.kubernetes-kops-dev2-hillghost-com-b9a1c2c419a63029501e849a8b56bad1.id}"
  iam_instance_profile = "${aws_iam_instance_profile.masters-kops-dev2-hillghost-com.id}"
  security_groups = ["${aws_security_group.masters-kops-dev2-hillghost-com.id}"]
  associate_public_ip_address = false
  user_data = "${file("data/aws_launch_configuration_master-us-west-2a.masters.kops-dev2.hillghost.com_user_data")}"
  root_block_device = {
    volume_type = "gp2"
    volume_size = "${var.master_root_block_device_vol_size}"
    delete_on_termination = true
  }
  ephemeral_block_device = {
    device_name = "/dev/sdc"
    virtual_name = "ephemeral0"
  }
  lifecycle = {
    create_before_destroy = true
  }
}

resource "aws_launch_configuration" "nodes-kops-dev2-hillghost-com" {
  name_prefix = "nodes.kops-dev2.hillghost.com-"
  image_id = "ami-66884c06"
  instance_type = "t2.medium"
  key_name = "${aws_key_pair.kubernetes-kops-dev2-hillghost-com-b9a1c2c419a63029501e849a8b56bad1.id}"
  iam_instance_profile = "${aws_iam_instance_profile.nodes-kops-dev2-hillghost-com.id}"
  security_groups = ["${aws_security_group.nodes-kops-dev2-hillghost-com.id}"]
  associate_public_ip_address = false
  user_data = "${file("data/aws_launch_configuration_nodes.kops-dev2.hillghost.com_user_data")}"
  root_block_device = {
    volume_type = "gp2"
    volume_size = "${var.nodes_root_block_device_vol_size}"
    delete_on_termination = true
  }
  lifecycle = {
    create_before_destroy = true
  }
}

resource "aws_route" "0-0-0-0--0" {
  route_table_id = "${aws_route_table.kops-dev2-hillghost-com.id}"
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = "${var.aws_nat_gateway_id}"
}

resource "aws_route_table" "kops-dev2-hillghost-com" {
  vpc_id = "${var.aws_vpc_id}"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "kops-dev2.hillghost.com"
  }
}

resource "aws_route_table_association" "us-west-2a-kops-dev2-hillghost-com" {
  subnet_id = "${aws_subnet.us-west-2a-kops-dev2-hillghost-com.id}"
  route_table_id = "${aws_route_table.kops-dev2-hillghost-com.id}"
}

resource "aws_route_table_association" "us-west-2b-kops-dev2-hillghost-com" {
  subnet_id = "${aws_subnet.us-west-2b-kops-dev2-hillghost-com.id}"
  route_table_id = "${aws_route_table.kops-dev2-hillghost-com.id}"
}

resource "aws_route_table_association" "us-west-2c-kops-dev2-hillghost-com" {
  subnet_id = "${aws_subnet.us-west-2c-kops-dev2-hillghost-com.id}"
  route_table_id = "${aws_route_table.kops-dev2-hillghost-com.id}"
}

resource "aws_security_group" "masters-kops-dev2-hillghost-com" {
  name = "masters.kops-dev2.hillghost.com"
  vpc_id = "${var.aws_vpc_id}"
  description = "Security group for masters"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "masters.kops-dev2.hillghost.com"
  }
}

resource "aws_security_group" "nodes-kops-dev2-hillghost-com" {
  name = "nodes.kops-dev2.hillghost.com"
  vpc_id = "${var.aws_vpc_id}"
  description = "Security group for nodes"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "nodes.kops-dev2.hillghost.com"
  }
}

resource "aws_security_group_rule" "all-master-to-master" {
  type = "ingress"
  security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  source_security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  from_port = 0
  to_port = 0
  protocol = "-1"
}

resource "aws_security_group_rule" "all-master-to-node" {
  type = "ingress"
  security_group_id = "${aws_security_group.nodes-kops-dev2-hillghost-com.id}"
  source_security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  from_port = 0
  to_port = 0
  protocol = "-1"
}

resource "aws_security_group_rule" "all-node-to-master" {
  type = "ingress"
  security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  source_security_group_id = "${aws_security_group.nodes-kops-dev2-hillghost-com.id}"
  from_port = 0
  to_port = 0
  protocol = "-1"
}

resource "aws_security_group_rule" "all-node-to-node" {
  type = "ingress"
  security_group_id = "${aws_security_group.nodes-kops-dev2-hillghost-com.id}"
  source_security_group_id = "${aws_security_group.nodes-kops-dev2-hillghost-com.id}"
  from_port = 0
  to_port = 0
  protocol = "-1"
}

resource "aws_security_group_rule" "https-external-to-master" {
  type = "ingress"
  security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "master-egress" {
  type = "egress"
  security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  from_port = 0
  to_port = 0
  protocol = "-1"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "node-egress" {
  type = "egress"
  security_group_id = "${aws_security_group.nodes-kops-dev2-hillghost-com.id}"
  from_port = 0
  to_port = 0
  protocol = "-1"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "ssh-external-to-master" {
  type = "ingress"
  security_group_id = "${aws_security_group.masters-kops-dev2-hillghost-com.id}"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "ssh-external-to-node" {
  type = "ingress"
  security_group_id = "${aws_security_group.nodes-kops-dev2-hillghost-com.id}"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_subnet" "us-west-2a-kops-dev2-hillghost-com" {
  vpc_id = "${var.aws_vpc_id}"
  cidr_block = "172.20.128.0/21"
  availability_zone = "us-west-2a"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "us-west-2a.kops-dev2.hillghost.com"
  }
}

resource "aws_subnet" "us-west-2b-kops-dev2-hillghost-com" {
  vpc_id = "${var.aws_vpc_id}"
  cidr_block = "172.20.136.0/21"
  availability_zone = "us-west-2b"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "us-west-2b.kops-dev2.hillghost.com"
  }
}

resource "aws_subnet" "us-west-2c-kops-dev2-hillghost-com" {
  vpc_id = "${var.aws_vpc_id}"
  cidr_block = "172.20.144.0/21"
  availability_zone = "us-west-2c"
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "us-west-2c.kops-dev2.hillghost.com"
  }
}

/*resource "aws_vpc" "kops-dev2-hillghost-com" {
  cidr_block = "172.20.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "kops-dev2.hillghost.com"
  }
}*/

/*resource "aws_vpc_dhcp_options" "kops-dev2-hillghost-com" {
  domain_name = "us-west-2.compute.internal"
  domain_name_servers = ["AmazonProvidedDNS"]
  tags = {
    KubernetesCluster = "kops-dev2.hillghost.com"
    Name = "kops-dev2.hillghost.com"
  }
}

resource "aws_vpc_dhcp_options_association" "kops-dev2-hillghost-com" {
  vpc_id = "${var.aws_vpc_id}"
  dhcp_options_id = "${aws_vpc_dhcp_options.kops-dev2-hillghost-com.id}"
}*/
