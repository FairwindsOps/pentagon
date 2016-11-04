ClusterGroup: production


How are environments specified.

In this example, there should be multiple environments in the working cluster, and a single production environment
in the production cluster. The working cluster should share a single RDS instance, and each have their own redis
instances

## Spec
working cluster:
  envs:
    demo
    qa1
    qa2
    dev  

contexts are clusters + namespaces and with namespaces being unique, they uuniquely identify clusters as well
such that:
kubectl config set-context $branchname --cluster working --namespace $branchname


clusters/
  working/
    cluster-config/ # aka terraform-kops-cluster
      # the stuff that manages the cluster itself, not what is inside it
      kubernetes.tf # creates the cluster # not next to terraform-vpc?
      kops files
    additional-resources/  # I don't love the name here. Perhaps `assets`, `resources`, `services`?
      # typically ansible here. Additional resources *for the Cluster* - Notably, if the client needed resources
      that weren't cluster dependencies, like Lambda + DynamoDB, that would not go here
      rds.yml # shared RDS across the cluster
      security-groups.yml
      db-subnet-groups.yml
    kubernetes/
      # Cluster administration kube API config files
      addons.yml
      namespaces.yml # specifies the namespaces that should exist and their respective quotas
    namespaces/
      # namespace level resources- no "env" specified per se since a namespace is 1:1 with environments
      demo/
        # Note that applications themselves do not belong here, this is the cluster administration level, not the
        # application owner's domain. An app owner trying to deploy to a namespace that does not exist should return an
        # error
        redis.yml
        # Also note that a service external to the cluster can't be opened to a namespace. Even though this redis.yml
        is in `namespaces/demo/`, that redis instances is opened to the working cluster. It's in the `namespaces` dir
        for conf file organization only. It should be thought of as `clusters/working/additional-resources/demo-redis.yml`
        buckets.yml
        ...
      qa1/
        redis.yml
      qa2/
        redis.yml



# What do the SGs look like exactly?
per cluster ($string):
  $string-master
    just the master ASG
  $string-nodes
    the node ASG. It's analogous to the '-application' SG
    This and the above master SG are created via kops/tf. The rest via additional-resources/security-groups.yml
  $string-data
    rds, redis to be opened to the $string cluster
  $string-internal-presentation
    internal ELBs
  $string-external-presentation
    public facing ELBs
