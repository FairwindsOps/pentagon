# Kubernetes Add-ons

## Dashboard

* Accessible at `https://MASTER/ui`. For hillghost: [https://api.hillghost-prod.hillghost.com](https://api.hillghost-prod.hillghost.com)

## Kibana
TODO: Needs to be updated with current instructions for ELK as `kops` does not automatically install logging/monitoring environment.

* `kubectl cluster-info` will display add-on details related to the ELK pods. For hillghost: https://api.hillghost-prod.hillghost.com/api/v1/proxy/namespaces/kube-system/services/kibana-logging
