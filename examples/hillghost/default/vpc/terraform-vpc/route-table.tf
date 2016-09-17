# Routing table for public subnets
resource "aws_route_table" "public" {
  vpc_id = "${aws_vpc.default.id}"
    route {
      cidr_block = "0.0.0.0/0"
      gateway_id = "${aws_internet_gateway.default.id}"
    }
  tags {
    Name = "public"
  }
}

# Routing table for private subnets
# Populates `instance_id` if NAT instances or `nat_gateway_id` if NAT
# Gateways were enabled via variable flags and created via TF.
resource "aws_route_table" "private" {
  count = "${var.az_count}"
  vpc_id = "${aws_vpc.default.id}"
  route {
    cidr_block = "0.0.0.0/0"
    /*instance_id = "${element(aws_instance.nat.*.id, count.index)}"*/
    nat_gateway_id = "${element(aws_nat_gateway.nat_gateway.*.id, count.index)}"
  }
  tags {
      Name = "private_az${(count.index +1)}"
  }
}
