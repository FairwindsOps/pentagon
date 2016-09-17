resource "aws_nat_gateway" "nat_gateway" {
  count = "${var.az_count * var.nat_gateway_enabled}"
  subnet_id = "${element(aws_subnet.public.*.id, count.index)}"
  allocation_id = "${element(aws_eip.mod_nat.*.id, count.index)}"
  depends_on = ["aws_internet_gateway.default","aws_eip.mod_nat","aws_subnet.public"]
}
