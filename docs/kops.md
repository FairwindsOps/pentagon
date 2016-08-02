# Building a cluster with Kops

## Basic Setup
* This gets you an RO-style VPC, with a kube cluster inside that VPC.
  * Some cluster details:
    * The cluster master and nodes are not in a [private subnet](https://github.com/kubernetes/kops/issues/220).
    * The addons are not [automatically installed](https://github.com/kubernetes/kops/issues/243)
    * This example is for a single master. HA master setups are supported. `etcd` needs a quorum of an odd number of instances, hence, a minimum of 3. See [Run with a HA master](https://github.com/kubernetes/kops/blob/master/README.md#other-interesting-modes)
* For a working example, see [dev-infra](https://github.com/reactiveops/dev-infra).

## Prerequisites

* kops is installed and in your PATH. See https://github.com/kubernetes/kops#installation
* NAME is chosen as described [here](https://github.com/kubernetes/kops#bringing-up-a-cluster-on-aws)


## Steps

* `pip install pentagon`
* `pentagon-startproject -n hillghostdev; cd hillghostdev;`
* Optionally, `git init` # and related version control steps
* Choose and set env vars:

```
export KOPS_STATE_STORE_BUCKET="hillghost-kops-state"
aws s3 mb s3://$KOPS_STATE_STORE_BUCKET #if needed
export NAME=hillghostdev.hillghost.com
export KOPS_STATE_STORE=s3://${KOPS_STATE_STORE_BUCKET}
export KUBECONFIG="$(pwd)/config/private/kube_config"
export ZONES="us-west-2a,us-west-2b,us-west-2c"

# unclear how this is used:
export SSH_KEY_PATH="/Users/justin/Documents/work/reactive/workspace/projects/kubernetes-demo/dev-infra/config/private/devkey.pub"
```

* Create the VPC
  * Ensure that the name of the created VPC matches $NAME. This is achieved by setting `aws_vpc_name` in `terraform.tfvars`, on the `kops` branch of `terraform-vpc`

```
cd hillghostdev/default/terraform
terraform plan -module-depth=-1 -var-file terraform.tfvars -out terraform.tfplan
terraform apply terraform.tfplan
# Makefile with remote config is fine, just not used for testing
```

* Get the VPC ID

```
export VPC_ID=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values="$NAME" |jq ."Vpcs"[0]."VpcId")
# Double check the value, the above jq just gets the first- if there are 2 vpcs with the same name, you may get the wrong one
```

* Create cluster config

```
kops create cluster \
--ssh-public-key $SSH_KEY_PATH \
--zones=$ZONES ${NAME} \
--vpc=$VPC_ID \
--network-cidr=172.20.0.0/16
```

* kops edit

`kops edit cluster ${NAME}`

* set the zone CIDRs (aka subnets) appropriately
  * See [Kubernetes Subnets](https://docs.google.com/spreadsheets/d/1w9PaEymkI-DE0QvSUQz-ExHhslDx7C0rLqpQY3sGW5w/edit#gid=0) for details.

* Run `kops update`

`kops update cluster --ssh-public-key $SSH_KEY_PATH ${NAME} --yes`

* Wait and verify. Output should looks similar to the below:

```
$ kubectl get nodes
NAME                                           STATUS                     AGE
ip-172-20-130-124.us-west-2.compute.internal   Ready                      25m
ip-172-20-133-45.us-west-2.compute.internal    Ready,SchedulingDisabled   25m
ip-172-20-139-213.us-west-2.compute.internal   Ready                      25m
```
```
$ kubectl cluster-info
Kubernetes master is running at https://api.kops-dev.hillghost.com
KubeDNS is running at https://api.kops-dev.hillghost.com/api/v1/proxy/namespaces/kube-system/services/kube-dns

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```



## Notes
* Drop the def cooldown on the master ASG
* How does master DNS work? It totally works, but I don't see how. user-data script?
* Run through, test and document HA master.

## To Do / To Decide
* How to represent this as infrastructure-as-code? The kops operations leave very little infrastructural code behind for the next operator to see. Initially, it can be a note in clusters/readme.md & vars in account/vars.sh
