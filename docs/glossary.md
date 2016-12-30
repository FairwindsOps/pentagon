# Glossary

_These terms are inspired by and borrow from [Kubernetes.io](kubernetes.io) and where applicable have been customized for ReactiveOps usage._
## Cluster
A Cluster is the set of servers that comprise a single Kubernetes Cluster. That is, it is managed from a single
(optionally load balanced) Kubernetes API. Examples: 'production', 'working'

## Namespaces
Kubernetes Namespaces are "virtual clusters" backed by a single physical cluster.

A typical configration would likely have Namespaces such as `default`, `production`, `dev`, `staging`, and the internal `kube-system`. Namespaces allow you to segregate resources into discrete environments.

Aside from 'default' and 'kube-system', a Namespace (in pentagon) should be
unique across clusters, and 1:1 with long-running environments. Nothing should be in the 'default' namespace

If you are operating on resources in any Namespace other than `default`, you must explicitly name it:
`$ kubectl --namespace=<insert-namespace-name-here> get pods`

### Context
In pentagon, Kubernetes contexts are pointers to Namespaces. Since Namespaces are unique members of clusters, they point to a cluster as well. These are defined in the kube_config file as needed:
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

You can also get `kubectl` to configure your kube_config file:

`$ kubectl config set-context hillghost-prod.hillghost.com --namespace=production`
`$ kubectl config view | grep namespace`

To switch contexts:
`$ kubectl config use-context production`

## Environment
An Environment is a logical grouping of a set of services, typically referred to as a stack or microservice, associated with a single application repository that is designed to be network-reachable to each other and segregated otherwise, except for the service(s) it (purposely) provides. In a Kubernetes on AWS infrastructure, an Environment may include an RDS instance, an Elasticache cluster, and a set of Kubernetes pods, containers, services, jobs in a namespace.

## Deployment
A Deployment provides declarative updates for Pods and Replica Sets. Once the desired state has been set in a Deployment object, the Deployment controlled will ensure the actual state and desired state remain consistent. This means that if a Pod crashes, the Deployment controller will schedule another to take its place, and you can scale Deployments up and down easily.

## Services
A Service is an abstraction which defines a logical set of Pods and a policy by which they may be accessed. This is necessary because any individual Kubernetes Pod is mortal and may move from node to node, crash and restart, or be scaled down or up. Services dynamically keep track of the list of Pods and provide a consistent address for this service.

>As an example, consider an image-processing backend which is running with 3 replicas. Those replicas are fungible - frontends do not care which backend they use. While the actual Pods that compose the backend set may change, the frontend clients should not need to be aware of that or keep track of the list of backends themselves. The Service abstraction enables this decoupling.

## Provisional: (Should this be here?)
"cluster-group": A resource, external to a Kubernetes cluster that is designed to be accessible by services in a particular namespace are said to be in that namespace's parent's cluster "cluster-group"
  For example. The `dev`, `staging` and `demo` environments all are environments with corresponding namespaces in the working cluster. Their dependent RDS instance would be said to be in the working cluster-group
