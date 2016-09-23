Kops + Terraform

# Run kops to generate terraform files

(This is for the second and any additional clusters)
keep in mind:
there will be a new route table created, with its 0/0 route
kops get clusters
kops delete cluster hillghostdev2.hillghost.com
New cluster, existing VPC:
(Cluster) name: hillghost-prod
mkdir default/clusters/hillghost-prod
updated default/clusters/hillghost-prod/vars.sh
source default/clusters/hillghost-prod/vars.sh

    kops create cluster \
    --ssh-public-key $SSH_KEY_PATH \
    --zones=$ZONES  \
    --network-cidr=172.20.0.0/16 \
    --target=terraform \
    ${NAME}
# Edit terraform files
- These are (TODO: slightly out of date) the steps that were taken to go from kops’ terraform output to what is in [examples/hillghost/default/clusters/production/cluster-config](https://github.com/reactiveops/pentagon/tree/example/examples/hillghost/default/clusters/production/cluster-config)
- `cp out/terraform/kubernetes.tf out/terraform/kubernetes.tf.orig`
- create and populate out/terraform/variables.tf


## in kubernetes.tf:
1. comment out the resource `"aws_internet_gateway"...` and the `resource "aws_vpc"` blocks
2. replace the vpc_id occurrences. Via regexes:
    find:
    vpc_id = "\${aws_vpc\..*\.id}"
    replace:
    vpc_id = "${var.aws_vpc_id}"
3. In the LCs, set associate_public_ip_address to false:
    find:
    associate_public_ip_address = true
    replace:
    associate_public_ip_address = false
4. Set the `resource "aws_route" "0-0-0-0--0"` to use the NAT gateway:
    find:
    gateway_id = "\$\{.*\.id\}"
    replace:
    nat_gateway_id = "${var.aws_nat_gateway_id}"
5. Choose the CIDRs that the subnets will use. See the [spreadsheet](https://docs.google.com/spreadsheets/d/1w9PaEymkI-DE0QvSUQz-ExHhslDx7C0rLqpQY3sGW5w/edit) for help. There should be 3x `resource "aws_subnet"` sections that will need their CIDRs edited:

For example: `cidr_block = "172.20.128.0/21"`

# ELB
  1. ELB is created via `elb.tf`
# Set up remote config to s3, plan, apply…etc

TODO:  add details here
$ terraform plan -out terraform.tfplan
$ terraform apply terraform.tfplan
