# Overview

For the demo client, there is:

## Clusters
Cluster 1: hillghost-prod.hillghost.com  (prod)
Cluster 2: kops-dev2.hillghost.com       (working)

## Namespaces
*  production: in the `prod` cluster
*  development: in the `working` cluster
*  staging: in the `working` cluster
*  (Note all Kubernetes clusters have `default` and `kube-system`)

## Environments:
* development
* staging
* production

## Contexts:
 * Since contexts are namespaces associated with clusters, there are 3 contexts defined.
