
A cluster is the set of servers that comprise a single Kubernetes cluster. That is, it is managed from a single
(optionally load balanced) Kubernetes API. Examples: 'production', 'working'

A namespace is a Kubernetes Namespace (default, production, dev, staging, kube-system)
  Aside from 'default' and 'kube-system', a namespace (in pentagon) should be unique across clusters, and 1:1 with long-running environments. Nothing should be in the 'default' namespace

An environment is a logical grouping of a set of services, typically referred to as a stack or microservice, associated with a single application repository that is designed to be network-reachable to each other and segregated otherwise, except for the service(s) it (purposely) provides. ~~In a Kubernetes on AWS infrastructure, an environment may include an RDS instance, an Elasticache cluster, and a set of Kubernetes pods, containers, services, jobs in a namespace~~

In pentagon, Kubernetes contexts are pointers to namespaces. Since namespaces are unique members of clusters, they point to a cluster as well. These are defined in the kube_config file as needed:
```
...
contexts:
- context:
    cluster: kops-dev2.hillghost.com
    namespace: development
    user: kops-dev2.hillghost.com
  name: development
- context:
    cluster: hillghost-prod.hillghost.com
    namespace: production
    user: hillghost-prod.hillghost.com
  name: production
- context:
    cluster: kops-dev2.hillghost.com
    namespace: staging
    user: kops-dev2.hillghost.com
  name: staging
current-context: production
...
```

Provisional:
"cluster-group": A resource, external to a Kubernetes cluster that is designed to be accessible by services in a particular namespace are said to be in that namespace's parent's cluster "cluster-group"
  For example. The dev, staging and demo environments all are environments with corresponding namespaces in the working cluster. Their dependent RDS instance would be said to be in the working cluster-group


For the demo client, there is:

## Clusters
Cluster 1: hillghost-prod.hillghost.com  (prod)
Cluster 2: kops-dev2.hillghost.com       (working)

## Namespaces

*  production: in the prod cluster
*  development: in the working cluster
*  staging: in the working cluster
*  (Note all Kubernetes clusters have default and kube-system

## Environments:
* development
* staging
* production

## Contexts:
 * Since contexts are namespaces associated with clusters, there are 3 contexts defined.


Cluster administrators vs. application owner


An application (read pods) are run in a namespace. That application, and any others in that namespace, together with any other additional resources comprise an environment.

Is there a diff bet env and namespace? Is "environment" meaningless and basically synonymous with namespace? The nuance is that an rds instance that is cluster-wide. It's definitely not correlated to an application's "environment"
settings eg. Rails' `config/environments/`
