# Monitoring

# Infrastructure Monitoring for DaaS Clients

* DaaS clients' infrastructure is monitored via an Icinga instance running on the ReactiveOps' main AWS account, accessible at:  [monitoring.reactiveops.io](https://monitoring.reactiveops.io/icingaweb2/)
* It uses Icinga's [distributed monitoring features](https://docs.icinga.com/icinga2/latest/doc/module/icinga2/toc#!/icinga2/latest/doc/module/icinga2/chapter/distributed-monitoring).
* The infrastructure as code repository for the Icinga instance is [reactiveops-infrastructure](https://github.com/reactiveops/reactiveops-infrastructure). It is inside that repo that the configuration files for the VPC and the instance running Icinga are.
* The monitoring configuration files are in [reactiveops-monitoring-configs](https://github.com/reactiveops/reactiveops-monitoring-configs). As of this writing, deploying the configuration is from an administrator's workstation, via `deploy/local-deplpoy.sh`

## Hydra
 * [Hydra](https://github.com/reactiveops/hydra) is the repository in which the Icinga Kubernetes client/agent is configured. It is run as a pod, designed to be one per cluster, via a Deployment. An example implementation is viewable in the Demo repository, in [default/clusters/working/kubernetes/hydra](https://github.com/reactiveops/demo-infrastructure/tree/master/default/clusters/working/kubernetes).
