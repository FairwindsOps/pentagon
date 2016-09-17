kops-notes

export GOPATH="/Users/justin/Documents/work/reactive/workspace/projects/kubernetes-demo/gocode/"

export KOPS_STATE_STORE_BUCKET="hillghost-kops-state"
aws s3 mb s3://$KOPS_STATE_STORE_BUCKET
export NAME=kops.hillghost.com
export KOPS_STATE_STORE=s3://${KOPS_STATE_STORE_BUCKET}


${GOPATH}/bin/kops create cluster --ssh-public-key "hillghost-infrastructure/config/private/working_kube_aws_rsa.pub" --cloud=aws --zones=us-east-1b,us-east-1c,us-east-1e ${NAME}

${GOPATH}/bin/kops update cluster --ssh-public-key "hillghost-infrastructure/config/private/working_kube_aws_rsa.pub" ${NAME} --yes


---
can I use terraform-vpc & kops?
dev in us-west-1
- create vpc in us-west-1
- create multi master, multizone kluster in that vpc
  - kluster not in a private subnet

...run `terraform apply`...

export KOPS_STATE_STORE_BUCKET="hillghost-kops-state"
#aws s3 mb s3://$KOPS_STATE_STORE_BUCKET
export NAME=kops-dev.hillghost.com
export KOPS_STATE_STORE=s3://${KOPS_STATE_STORE_BUCKET}
export SSH_KEY_PATH="/Users/justin/Documents/work/reactive/workspace/projects/kubernetes-demo/dev-infra/config/private/devkey.pub"
export ZONES="us-west-1b,us-west-1c"
export VPC_ID="vpc-7abe8d1f"  #get the VPC ID
${GOPATH}/bin/kops create cluster --ssh-public-key $SSH_KEY_PATH --zones=$ZONES ${NAME} \
--vpc=$VPC_ID --network-cidr=172.20.0.0/16

kops edit cluster ${NAME}
      - set the zone CIDRs (aka subnets appropriately)- in my dev example, I used the CIDRs from admin_az[1,2] and deleted them

kops update cluster --ssh-public-key $SSH_KEY_PATH ${NAME} --yes

Note: The KUBECONFIG env var is respected


----


* For an HA master: etcd needs a quorum of an odd number of instances, hence, a minimum of 3. So, a
