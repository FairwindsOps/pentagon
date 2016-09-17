resource "aws_instance" "nat" {
  count = "${var.az_count * var.nat_instance_enabled}"
  ami = "${lookup(var.aws_nat_ami, var.aws_region)}"
  instance_type = "${var.nat_instance_type}"
  key_name = "${var.nat_key_name}"
  security_groups = ["${aws_security_group.nat.id}"]
  /*subnet_id = "${element(aws_subnet.public.*.id, count.index)}"*/
  associate_public_ip_address = true
  source_dest_check = false
  tags {
    Name = "admin_nat_az${(count.index + 1)}"
  }
}
