# Building a cluster with Kops

## Basic Setup
* This gets you an RO-style VPC, with a Kubernetes cluster inside that VPC.
  * Some cluster details:
    * The cluster master and nodes are in private subnets.
    * This example is for a single master. HA master setups are supported. `etcd` needs a quorum of an odd number of instances, hence, a minimum of 3. See [Run with a HA master](https://github.com/kubernetes/kops/blob/master/README.md#other-interesting-modes)
* For a working example, see [demo-infrastructure](https://github.com/reactiveops/demo-infrastructure).

## Prerequisites

* Install `kubectl`. As of 25 Jan 2017, we assume kubectl version 1.5.2.
	- On OSX, you can brew update && brew install kubectl.
	- Otherwise, visit the [kubectl installation docs](https://kubernetes.io/docs/user-guide/prereqs/)
	- You may find kubectl bash completion useful- the instructions are in the same link above.
	- Related: AWS completion can also be very useful: [AWS completion instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-command-completion.html)
* Install [kops](https://github.com/kubernetes/kops) v1.5.0-alpha4 (as of Jan 24, 2017).

## Steps

* `pip install pentagon`
* `pentagon-startproject -n <projectname>; cd <projectname>;`
* `git init`
* Create a VPC via `default/vpc`. See [docs/vpc](vpc.md).
* Follow instructions in `config/local/vars` and fill in the necessary details.
* Generate an ssh key for the new cluster
  * `ssh-keygen` and save the file in `config/private/<cluster-type>` (production/working)
  ie: `export SSH_KEY_PATH="${HOME}/workspace/projects/<projectname>/<projectname>-infrastructure/config/private/production.pub`
* Set the location that you would like to write your kube_config file to via `export KUBECONFIG=${INFRASTRUCTURE_REPO}/config/private/kubeconfig`
* Examine and complete steps in: `default/clusters/production/cluster-config/kops.sh`.
