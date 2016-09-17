
resource "aws_security_group" "master-elb-hillghost-prod-hillghost-com" {
  name = "master-elb.hillghost-prod.hillghost.com"
  vpc_id = "${var.aws_vpc_id}"
  description = "Security group for master ELB"
  tags = {
    KubernetesCluster = "hillghost-prod.hillghost.com"
    Name = "master-elb.hillghost-prod.hillghost.com"
  }
}

resource "aws_security_group_rule" "all-public-to-master-elb" {
  type = "ingress"
  security_group_id = "${aws_security_group.master-elb-hillghost-prod-hillghost-com.id}"
  from_port = 443
  to_port = 443
  cidr_blocks = ["0.0.0.0/0"]
  protocol = "tcp"
}

resource "aws_security_group_rule" "master-elb-to-public" {
  type = "egress"
  security_group_id = "${aws_security_group.master-elb-hillghost-prod-hillghost-com.id}"
  from_port = 443
  to_port = 443
  cidr_blocks = ["0.0.0.0/0"]
  protocol = "tcp"
}

resource "aws_elb" "master-elb-hillghost-prod-hillghost-com" {
  name = "master-elb-hillghost-prod"
  subnets = ["${var.vpc_public_az1_id}", "${var.vpc_public_az2_id}", "${var.vpc_public_az3_id}"  ]
  security_groups = ["${aws_security_group.master-elb-hillghost-prod-hillghost-com.id}"]
  listener {
    instance_port = 443
    instance_protocol = "tcp"
    lb_port = 443
    lb_protocol = "tcp"
  }

  tags {
    Name = "master-elb-hillghost-prod-hillghost-com"
  }
}


resource "aws_route53_record" "api-master" {
  zone_id = "${var.route53_name_zone_id}"
  name = "api.hillghost-prod.hillghost.com"
  type = "A"

  alias {
    name = "${aws_elb.master-elb-hillghost-prod-hillghost-com.dns_name}"
    zone_id = "${aws_elb.master-elb-hillghost-prod-hillghost-com.zone_id}"
    evaluate_target_health = false
  }
}
