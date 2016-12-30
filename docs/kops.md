# Building a cluster with Kops

## Basic Setup
* This gets you an RO-style VPC, with a Kubernetes cluster inside that VPC.
  * Some cluster details:
    * The cluster master and nodes are in private subnets.
    * This example is for a single master. HA master setups are supported. `etcd` needs a quorum of an odd number of instances, hence, a minimum of 3. See [Run with a HA master](https://github.com/kubernetes/kops/blob/master/README.md#other-interesting-modes)
* For a working example, see [demo-infrastructure](https://github.com/reactiveops/demo-infrastructure).

## Prerequisites

* Install [kops](https://github.com/kubernetes/kops) v1.4.4 (as of Dec 20, 2016).

## Steps

* `pip install pentagon`
* `pentagon-startproject -n <projectname>; cd <projectname>;`
* Optionally, `git init` # and related version control steps

* Create a VPC via `default/vpc`. See [docs/vpc](vpc.md).

* Follow instructions in `config/local/vars` and fill in the necessary details.

* Generate an ssh key for the new cluster
  * `ssh-keygen` and save the file in `config/private/<cluster-type>` (production/working)
  ie: `export SSH_KEY_PATH="${HOME}/workspace/projects/<projectname>/<projectname>-infrastructure/config/private/production.pub`
* Set the location that you would like to write your kube_config file to via `export KUBECONFIG=${INFRASTRUCTURE_REPO}/config/private/<clustertype>-kubeconfig`
* Examine and complete steps in: `default/clusters/production/cluster-config/kops.sh`. 
