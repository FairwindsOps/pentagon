#!/bin/bash

source ../../../account/vars.sh
source ../vars.sh

## STEP 1

kops create cluster \
  --cloud aws \
  --topology private \
  --networking cni \
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
  --bastion=false

## Step 2
## Edit the cluster for the private VPC
## kops edit cluster $CLUSTER_NAME

# For example, this is how a 3-az subnet spec might look if you are installing on a fresh RO-style VPC.
#  subnets:
# - cidr: 172.20.120.0/21
#   name: us-east-1a
#   type: Private
#   zone: us-east-1a
# - cidr: 172.20.144.0/21
#   name: utility-us-east-1a
#   type: Utility
#   zone: us-east-1a
# - cidr: 172.20.128.0/21
#   name: us-east-1b
#   type: Private
#   zone: us-east-1b
# - cidr: 172.20.152.0/21
#   name: utility-us-east-1b
#   type: Utility
#   zone: us-east-1b
# - cidr: 172.20.136.0/21
#   name: us-east-1c
#   type: Private
#   zone: us-east-1c
# - cidr: 172.20.160.0/21
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

# Next, install weave-kube latest: `kubectl apply -f https://git.io/weave-kube`
# We install weave-kube here because setting the flag `--networking weave` currently uses a buggy version of weave that can cause DNS problems (12/21/2016)

# `kubectl get nodes`
# You should see your master and your worker nodes popping up. At first while weave-net propogates, you may only see master.
#
# If there are issues, `kubectl get pods --all-namespaces` may show you which pods are having a hard time starting up.
