aws_vpc_name = "<PLACEHOLDER>"
vpc_cidr_base = "172.20"
aws_azs = "<PLACEHOLDER>"
az_count = 3
# Substitute $INFRASTRUCTURE_REPO for your hardcoded path
# aws_inventory_path = "$INFRASTRUCTURE_REPO/plugins/inventory"
aws_inventory_path =  "<PLACEHOLDER>"
aws_region = "<PLACEHOLDER>"

admin_subnet_parent_cidr = ".0.0/22"
admin_subnet_cidrs = {
    zone0 = ".0.0/24"
    zone1 = ".1.0/24"
    zone2 = ".2.0/24"
    zone3 = ".3.0/24"
  }

public_subnet_parent_cidr = ".0.0/22"
public_subnet_cidrs = {
    zone0 = ".4.0/24"
    zone1 = ".5.0/24"
    zone2 = ".6.0/24"
    zone3 = ".7.0/24"
  }

private_prod_subnet_parent_cidr = ".0.0/22"
private_prod_subnet_cidrs = {
    zone0 = ".8.0/24"
    zone1 = ".9.0/24"
    zone2 = ".10.0/24"
    zone3 = ".11.0/24"
  }

private_working_subnet_parent_cidr = ".0.0/22"
private_working_subnet_cidrs = {
    zone0 = ".12.0/24"
    zone1 = ".13.0/24"
    zone2 = ".14.0/24"
    zone3 = ".15.0/24"
  }
