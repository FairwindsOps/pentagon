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

```
kops create cluster \
--ssh-public-key $SSH_KEY_PATH \
--zones=$ZONES  \
--network-cidr=172.20.0.0/16 \
--target=terraform \
${NAME}
```

cp out/terraform/kubernetes.tf  out/terraform/kubernetes.tf.orig
create and populate out/terraform/variables.tf
in kubernetes.tf:
 1. comment out the resource `"aws_internet_gateway"...` and the `resource "aws_vpc"` blocks
 2. replace the vpc_id occurences. Via regexes:
```
find:
vpc_id = "\${aws_vpc\..*\.id}"
replace:
vpc_id = "${var.aws_vpc_id}"
```


In the LCs, set associate_public_ip_address to false:
```
find:
associate_public_ip_address = true
replace:
associate_public_ip_address = false
```

Set the `resource "aws_route" "0-0-0-0--0"` to use the NAT gateway:
```
find:
gateway_id = "\$\{.*\.id\}"
replace:
nat_gateway_id = "${var.aws_nat_gateway_id}"
```

Choose the CIDRs that the subnets will use. See the spreadsheet for help. There should be 3x `resource "aws_subnet"` that will need their CIDRs edited:
eg. `cidr_block = "172.20.128.0/21" `

# remote config
$ terraform plan -out terraform.tfplan
$ terraform apply terraform.tfplan

~~Create an ELB
# ELB for master
1. SG for ELB: hillghost-prod-hillghost-com
(2. master sg needs to allow in from the elb's sg
  * actually, it's allow all 443 now. that needs to change.)
3. ELB creation itself
4. DNS record tied to ELB (required due to cert matching)
  1. api.hillghost-prod.hillghost.com as an A ALIAS -->  the ELB~~

ELB is created via elb.tf. Note: add `load_balancers = ["${aws_elb.master-elb-hillghost-prod-hillghost-com.name}"]` to kubernetes.tf



## Issues:
it looks to me that kops doesn't support 2 clusters in same VPC?
Issues: the VPC Name tag- what should it be?



##  kops create output:

$ kops create cluster \
> --ssh-public-key $SSH_KEY_PATH \
> --zones=$ZONES  \
> --network-cidr=172.20.0.0/16 \
> --target=terraform \
> ${NAME}
I0905 16:42:18.667177   73581 create_cluster.go:309] Inferred --cloud=aws from zone "us-west-2a"
I0905 16:42:18.667556   73581 cluster.go:364] Assigned CIDR 172.20.32.0/19 to zone us-west-2a
I0905 16:42:18.667579   73581 cluster.go:364] Assigned CIDR 172.20.64.0/19 to zone us-west-2b
I0905 16:42:18.667592   73581 cluster.go:364] Assigned CIDR 172.20.96.0/19 to zone us-west-2c
I0905 16:42:19.046622   73581 cluster.go:340] Using kubernetes latest stable version: v1.3.6
W0905 16:42:19.050434   73581 populate_cluster_spec.go:225] Normalizing kubernetes version: "v1.3.6" -> "1.3.6"
I0905 16:42:19.987326   73581 populate_cluster_spec.go:239] Defaulting DNS zone to: Z2TQO6PXZ7B48Y
I0905 16:42:21.016722   73581 apply_cluster.go:110] Adding default kubelet release asset: https://storage.googleapis.com/kubernetes-release/release/v1.3.6/bin/linux/amd64/kubelet
I0905 16:42:21.260667   73581 apply_cluster.go:505] Found hash "1ba78f5ec8cc672d6232429bb74ef11bd53e3e5b" for "https://storage.googleapis.com/kubernetes-release/release/v1.3.6/bin/linux/amd64/kubelet"
I0905 16:42:21.260732   73581 apply_cluster.go:121] Adding default kubectl release asset: https://storage.googleapis.com/kubernetes-release/release/v1.3.6/bin/linux/amd64/kubectl
I0905 16:42:21.536962   73581 apply_cluster.go:505] Found hash "305843f124319fd8cff2a4133a66df0bad76a374" for "https://storage.googleapis.com/kubernetes-release/release/v1.3.6/bin/linux/amd64/kubectl"
I0905 16:42:21.537075   73581 apply_cluster.go:148] Using default nodeup location: "https://kubeupv2.s3.amazonaws.com/nodeup/nodeup-1.3.tar.gz"
I0905 16:42:22.075559   73581 executor.go:68] Tasks: 0 done / 51 total; 22 can run
I0905 16:42:22.079040   73581 dnszone.go:155] Check for existing route53 zone to re-use with name "Z2TQO6PXZ7B48Y"
I0905 16:42:22.144971   73581 dnszone.go:162] Existing zone "hillghost.com." found; will configure TF to reuse
I0905 16:42:22.792344   73581 vfs_castore.go:384] Issuing new certificate: "master"
I0905 16:42:23.023267   73581 vfs_castore.go:384] Issuing new certificate: "kubecfg"
I0905 16:42:23.024573   73581 vfs_castore.go:384] Issuing new certificate: "kubelet"
I0905 16:42:25.109271   73581 executor.go:68] Tasks: 22 done / 51 total; 12 can run
I0905 16:42:25.110746   73581 executor.go:68] Tasks: 34 done / 51 total; 15 can run
I0905 16:42:25.495843   73581 executor.go:68] Tasks: 49 done / 51 total; 2 can run
I0905 16:42:25.496106   73581 executor.go:68] Tasks: 51 done / 51 total; 0 can run
I0905 16:42:25.502226   73581 target.go:165] Terraform output is in out/terraform
I0905 16:42:25.502378   73581 create_cluster.go:419] Exporting kubecfg for cluster
Wrote config for hillghost-prod.hillghost.com to "/Users/justin/workspace/projects/kubernetes-demo/dev-infra/config/private/kube_config"
