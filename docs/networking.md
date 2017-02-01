# Networking
This document is the source of knowledge for pentagon style network configuration. We create a base VPC with [terraform-vpc](https://github.com/reactiveops/terraform-vpc) that allocates capacity for AWS-based resources that a client needs to host, including `kubernetes`. We then let `kops` work in the same VPC to carve out a dedicated space for itself so that `kubernetes` is self-contained and manageable.

## Network overview diagram
**TO COME**

## VPC
The VPC is created by Terraform VPC which sets up a standard RO-style network platform. `kops` is then used to configure and deploy `kubernetes` into this existing VPC.

## Subnets
Per AZ, terraform-vpc creates 4 subnets: 1 `admin`, 1 `public`, and 2 `private` (one `working` and one `production`). Use these subnets to deploy any resources other than those directly associated with `kubernetes`.

Let `kops` create dedicated public and private subnets that run in parallel to those created by terraform-vpc. In `kops edit cluster`, allocate CIDRs of available address space.

## NAT Gateways
NAT Gateways are created by terraform-vpc and one is needed for each AZ. You can share a NAT Gateway for use by `kubernetes` and your other AWS-based resources simultaneously. This is the only exception to the separation of `kops` and TF. During `kops edit cluster`, specify the NAT Gateway in the private subnet using the keyword `egress` as shown in the [kops Example networking spec](#kops-example-networking-spec).

## Route tables
terraform-vpc sets up route tables for all of the standard subnets. The `private` subnets default route for external traffic is the NAT Gateway in that zone. The `public` subnets default route is through an Internet Gateway.

`kops` manages the subnets for your `kubernetes` resources so it also manages these route tables. Specifying the NAT Gateway that terraform-vpc created in `egress` will configure the default routes for these subnets to its specified NAT Gateway.

Because NAT Gateways don't have tags on AWS, `kops` keeps track of this NAT Gateway by AWS-tagging the route table with K=V pair `AssociatedNatGateway=nat-05ee835341f099286`. This is for the delete logic in `kops` that likely wouldn't actually be able to delete the Gateway (because it would still be in use by other routes), but it would attempt to delete it as a "related resource".

## Tags
terraform-vpc tags all of the resources that it creates and manages as `Managed By=Terraform`. Likewise, `kops` tags the resources that it creates and manages with `KubernetesCluster=<clustername>`. By letting `kops` create its own subnets, `kops` related tags are all restricted to resources that are owned by `kops`, so terraform-vpc doesn't ever need to know about `kops` and vice versa.

## kops Example networking spec

```yaml
subnets:
- cidr: 172.20.136.0/21
  egress: nat-05ee835341f099286
  name: us-east-1a
  type: Private
  zone: us-east-1a
- cidr: 172.20.144.0/21
  egress: nat-0973eca2e99f9249c
  name: us-east-1c
  type: Private
  zone: us-east-1c
- cidr: 172.20.152.0/21
  egress: nat-015aa74ead665693d
  name: us-east-1d
  type: Private
  zone: us-east-1d
- cidr: 172.20.160.0/21
  name: utility-us-east-1a
  type: Utility
  zone: us-east-1a
- cidr: 172.20.168.0/21
  name: utility-us-east-1c
  type: Utility
  zone: us-east-1c
- cidr: 172.20.176.0/21
  name: utility-us-east-1d
  type: Utility
  zone: us-east-1d
```
