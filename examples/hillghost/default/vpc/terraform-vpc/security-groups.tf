# nat
resource "aws_security_group" "nat" {
  count = "${var.nat_instance_enabled}"
  name = "admin_nat"
  description = "Allow services from the private subnet through NAT"
  vpc_id = "${aws_vpc.default.id}"
  tags {
    Name = "admin_nat"
  }
}

resource "aws_security_group_rule" "nat_allow_http_to_world" {
  count = "${var.nat_instance_enabled}"
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_https_to_world" {
  count = "${var.nat_instance_enabled}"
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_ntp_to_world" {
  count = "${var.nat_instance_enabled}"
  type = "egress"
  from_port = 123
  to_port = 123
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_git_to_github" {
  count = "${var.nat_instance_enabled}"
  type = "egress"
  from_port = 9418
  to_port = 9418
  protocol = "tcp"
  cidr_blocks = ["192.30.252.0/22"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_ssh_to_github" {
  count = "${var.nat_instance_enabled}"
  type = "egress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["192.30.252.0/22"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_ping_to_world" {
  count = "${var.nat_instance_enabled}"
  type = "egress"
  from_port = -1
  to_port = -1
  protocol = "icmp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_ping_from_world" {
  count = "${var.nat_instance_enabled}"
  type = "ingress"
  from_port = -1
  to_port = -1
  protocol = "icmp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_all_tcp_traffic_from_vpc" {
  count = "${var.nat_instance_enabled}"
  type = "ingress"
  from_port = 1
  to_port = 65535
  protocol = "tcp"
  cidr_blocks = ["${aws_vpc.default.cidr_block}"]
  security_group_id = "${aws_security_group.nat.id}"
}

resource "aws_security_group_rule" "nat_allow_all_udp_traffic_from_vpc" {
  count = "${var.nat_instance_enabled}"
  type = "ingress"
  from_port = 1
  to_port = 65535
  protocol = "udp"
  cidr_blocks = ["${aws_vpc.default.cidr_block}"]
  security_group_id = "${aws_security_group.nat.id}"
}
