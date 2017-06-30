#!/bin/bash

source ../../../account/vars.sh
source ../vars.sh

## STEP 1
# Note: These instructions are based on kops 1.5.1
# kops 1.5.1 should be used for all installations of k8s 1.4.x and 1.5.x (2/17)

kops create cluster \
  --cloud aws \
  --topology private \
  --networking weave \
  --state $KOPS_STATE_STORE \
  --node-count $NODE_COUNT \
  --zones $ZONES \
  --master-zones $MASTER_ZONES \
  --dns-zone $DNS_ZONE \
  --node-size $NODE_SIZE \
  --master-size $MASTER_SIZE \
  -v $V_LOG_LEVEL \
  --ssh-public-key $SSH_KEY_PATH \
  --vpc $VPC_ID \
  --network-cidr $NETWORK_CIDR \
  --name $CLUSTER_NAME \
  --kubernetes-version=$KUBERNETES_VERSION \
  --bastion=false


## Step 2
## Edit the cluster for the private VPC
## kops edit cluster $CLUSTER_NAME

# This is how a 3-AZ subnet spec might look if you are installing on a fresh RO-style VPC created in 3-AZs.
# The VPC CIDR is 172.20.0.0/16

# For our situation, we should let kops create it's own private and public subnets.
# In private topology, kops is going to put masters and workers in private subnets. The only
# resources that will reside in what are called "utility" subnets below is the ELB that
# points to the API.

# subnets:
# - cidr: 172.20.16.0/24
#   egress: nat-05ee835341f099286
#   name: us-east-1a
#   type: Private
#   zone: us-east-1a
# - cidr: 172.20.17.0/24
#   egress: nat-0973eca2e99f9249c
#   name: us-east-1b
#   type: Private
#   zone: us-east-1b
# - cidr: 172.20.18.0/24
#   egress: nat-015aa74ead665693d
#   name: us-east-1c
#   type: Private
#   zone: us-east-1c
# - cidr: 172.20.20.0/24
#   name: utility-us-east-1a
#   type: Utility
#   zone: us-east-1a
# - cidr: 172.20.21.0/24
#   name: utility-us-east-1b
#   type: Utility
#   zone: us-east-1b
# - cidr: 172.20.22.0/24
#   name: utility-us-east-1c
#   type: Utility
#   zone: us-east-1c

## A useful resource is (here)[https://github.com/kubernetes/kops/blob/master/docs/run_in_existing_vpc.md]
## Req'd reading: (K8s subnet calc sheet)[https://reactiveops.slack.com/files/justin/F343TL5PE/kubernetes_subnets]

## Step 3

# kops update cluster $CLUSTER_NAME

## Review changes

# kops update cluster $CLUSTER_NAME --yes

## Step 4

# Let kops do its work behind the scenes. It takes a few minutes to get the ELBs healthy so that we can connect to the master.
# When `kubectl cluster-info` returns the location of the kubernetes master, you can proceed.

# `kubectl get nodes`
# You should see your master and your worker nodes popping up. At first while weave-net propogates, you may only see master.
#
# If there are issues, `kubectl get pods --all-namespaces` may show you which pods are having a hard time starting up.
