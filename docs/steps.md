# Specs

Region: us-west-2


# Steps

* mkproject micron
* mkdir micron-infrastructure
* set up core dir structure
* pip install -r config/requirements.txt
* In the RO-prime AWS account, created the `micron-operator` group, and added jmound to it

I didn't check in, nor set the submodule for the kubernetes vendor, but,
`~/workspace/projects/micron/micron-infrastructure/vendor/kubernetes/kubernetes/version` should exist.

## working cluster first. no VPC created yet
ran ./up.sh -it may failed. It ended with:
```
Generating certs for alternate-names: IP:52.39.87.64,IP:172.20.0.9,IP:10.0.0.1,DNS:kubernetes,DNS:kubernetes.default,DNS:kubernetes.default.svc,DNS:kubernetes.default.svc.cluster.local,DNS:working-master
Starting Master

A client error (InvalidIPAddress.InUse) occurred when calling the RunInstances operation: Address 172.20.0.9 is in use.
(micron) 588 justin:working$
```

ran clusters/working/down.sh
and ./up.sh again, and it succeeded completely.
went to https://52.39.203.160/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard to test

Added bin PATH
PATH=$PATH:~/workspace/projects/micron/micron-infrastructure/vendor/kubernetes/kubernetes/cluster/

I took the vpc id, and subnet id that was created, and used that to set it for production/vars.sh
---
cd production/ ; ./up.sh ; sn
I had a bunch of problems, since kube isn't designed to share a vpc with another cluster. It seems that all you need is to
override MASTER_INTERNAL_IP
This method throws a warning about using the same routing table.
Hint: the master IP is set on the master's EBS volume metdata tags also. So when taking down the cluster, you need to del that
volume as well when rebuilding.
So, all that needed to be done was the second set of vars
./down.sh seems to do nothing

killing the cluster:
kill master
kill LCs
kill asg
kill Routing tables
del EBS vols
release EIPs
---
2 klusters up.

--
switching context:
```
(micron) 655 justin:production$ kubectl.sh config use-context aws_working
switched to context "aws_working".
(micron) 656 justin:production$ kubectl.sh config use-context aws_production
switched to context "aws_production".
(micron) 657 justin:production$ kubectl.sh config use-context DNE
no context exists with the name: "DNE".
(micron) 658 justin:production$
```
---
st2:

ansible-galaxy install -r ansible-requirements-dev.yml

I got stuck on creating the st2 server, because networking / VPC / omnia is missing. I think it's easiest / best
to tread onward with no terraform-vpc, and install st2 in the same single sn, no ELB, and just customize the role as need be.

Ideally, I think, we might want st2 to sit alongside the kube native elk, grafana, etc.
and then we'd have an API from running st2 actions.
