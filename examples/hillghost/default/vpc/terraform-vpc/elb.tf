# Create a new load balancer
resource "aws_elb" "masters-kops-dev2-hillghost-com" {
  name = "masters-kops-dev2-hillghost-com"
  subnets = ["${aws_subnet.public.*.id}"]

  listener {
    instance_port = 443
    instance_protocol = "tcp"
    lb_port = 443
    lb_protocol = "tcp"
  }

  cross_zone_load_balancing = true
  security_groups = ["${aws_security_group.masters-elb-kops-dev2-hillghost-com.id}"]
  tags {
    Name = "masters.kops-dev2.hillghost.com"
  }
}


resource "aws_security_group" "masters-elb-kops-dev2-hillghost-com" {
  name = "masters-elb.kops-dev2.hillghost.com"
  description = "Allow master"
  vpc_id = "${aws_vpc.default.id}"
  tags {
    Name = "masters.kops-dev2.hillghost.com"
  }
}
resource "aws_security_group_rule" "masters_elb" {
  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.masters-elb-kops-dev2-hillghost-com.id}"
}

resource "aws_security_group_rule" "masters_allow_all" {
    type = "egress"
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    security_group_id = "${aws_security_group.masters-elb-kops-dev2-hillghost-com.id}"

}
