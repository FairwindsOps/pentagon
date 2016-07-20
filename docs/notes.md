# Installation

Currently pentagon relies on Kubernetes version 1.2. Downloading the default will likely produce bad results. The correct `kubernetes.tar.gz` to install is the most recent version of the 1.2 branch. Releases can be found at [https://github.com/kubernetes/kubernetes/releases](https://github.com/kubernetes/kubernetes/releases).

Download the correct version.

Then in the client repo create the `vendor/kubernetes` directory and place the [pentagon `get.sh`][https://github.com/reactiveops/pentagon/blob/dev/vendor/kubernetes/get.sh] in it. It's also possible to use the [official `get.sh`](https://get.k8s.io). Then untar the Kubernetes tarball in the same directory.

```bash
export KUBE_VERSION="v1.2.6"
mkdir "$INFRASTRUCTURE_REPO/vendor/kubernetes"
cd "$INFRASTRUCTURE_REPO/vendor/kubernetes"
curl -sS https://get.k8s.io > get.sh
curl -sL https://github.com/kubernetes/kubernetes/releases/download/"${KUBE_VERSION}"/kubernetes.tar.gz | tar axvf -
```

The final step requires the modification of `$INFRASTRUCTURE_REPO/vendor/kubernetes/kubernetes/cluster/aws/util.sh` with the following patch, which is specific for Kubernetes 1.2 and will likely have bad results if applied to another version. The patch essentially disables the use ofa public IP for the master and instead runs it hidden inside AWS.

```diff
268d267
<       echo "ENABLE_NODE_PUBLIC_IP is true"
271d269
<       echo "ENABLE_NODE_PUBLIC_IP is not true"
581d578
<       echo "setting KUBE_MASTER_IP to  ${MASTER_RESERVED_IP} "
586d582
<       echo "DEBUG An error occurred"
1105a1102
>     --associate-public-ip-address \
1118,1121c1115
<     # local ip=$(get_instance_public_ip ${master_id})
<     local ip=$MASTER_RESERVED_IP
<     echo "This is ip:"
<     echo $ip
---
>     local ip=$(get_instance_public_ip ${master_id})
1137c1131
<       # attach-ip-to-instance ${KUBE_MASTER_IP} ${master_id}
---
>       attach-ip-to-instance ${KUBE_MASTER_IP} ${master_id}
1145,1147d1138
<       echo "troubleshooting"
<       echo "$ROUTE_TABLE_ID $MASTER_IP_RANGE $master_id"
<       # aws ec2 create-route --route-table-id rtb-83cd82e7 --destination-cidr-block 10.246.0.0/24 --instance-id i-0558d60fb07e0e420
```

Save that as `util.diff` and apply via

```bash
patch -R "$INFRASTRUCTURE_REPO/vendor/kubernetes/kubernetes/cluster/aws/util.sh" util.diff
```

At this point everything should be ready to go from the Kubernetes tooling perspective.

# Configuration

Assuming that Terraform has been run to create the VPC and network structure, the Kubernetes cluster will need to be configured. Assuming just the *working* cluster now, this will mean editing the file `$INFRASTRUCTURE_REPO/default/clusters/working/vars.sh`. The variables to be modified are
- `KUBE_AWS_ZONE` set this to the the first AZ created via Terraform
- `VPC_ID` should be the VPC id created by Terraform
- `SUBNET_ID` is the id of the subnet for `private_working_az1`
- `MASTER_RESERVED_IP` should be an ip in the AZ and subnet set earlier, which will be dedicate to the Kubernetes master
- `EXTERNAL_DNS_NAME` is the domain that will be used to expose things

# Creating the Kubernetes cluster

To spin up the `working` Kubernetes cluster run

```bash
cd "$INFRASTRUCTURE_REPO/default/clusters/working/"
./up.sh
# then you wait
```

# Manual corrections

The default will produce one master and 4 minion instances living in `private_working_az1`. Since we are using the networking produced by Terraform, some manual adjustments are needed.

1. The Kubernetes `up.sh` will create it's on routing table which will be tagged with `KubernetesCluster: working`. This routing table will need to be associated with the `private_working_az1` subnet.
2. Update routing table tagged `KubernetesCluster: working` to point to the NAT gateway used by the `private_az1` routing table rather than the IGW for the default route of `0.0.0.0/0`

After that the minions should be able to reach the outside world so that they can retrieve docker images etc.

# What's the ELB for?

Since the Kubernetes cluster was set up without an external public IP address, there isn't a way to reach it easily. That's a problem for CircleCI. To avoid exposing the master to the internet directly and ELB serves as an intermediary. This opens up the possibility to use either the ELB address or the internal IP address when connected via VPN for `kubectl` commands. One caveat is that some of the kubectl commands requires HTTP/2, which will not work via the ELB. One example of this is the `kubectl exec` use case. This works fine via the IP over the VPN.
