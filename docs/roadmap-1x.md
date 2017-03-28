# Pentagon Roadmap, 1.x

## Project Management Notes
- Milestones are collections of Github issues.
- This roadmap is a high-level view of features, tracked as issues to be included in each milestone. A milestone will usually have other bugs, features, tasks as well.
- Features and ideas not in scope here should be added to the "[Upcoming](https://github.com/reactiveops/pentagon/milestone/5)" milestone.

## [1.0](https://github.com/reactiveops/pentagon/milestone/1)
- **Greenfield Turnkey Installations**: Clarifying a set of requirements and questions that, once answered, generate a default set of servers and services that is ready to be deployed to, and largely automated [#114](https://github.com/reactiveops/pentagon/issues/114)
- Provably reliable (scripted, possibly manually, but a repeatable method to verify this feature), demonstrable **autoscaling of the nodes** in a cluster: the ASG should add / delete nodes as demand dictates [#120](https://github.com/reactiveops/pentagon/pull/120)
- A scripted, (possibly manual) demonstration or test of **horizontal pod autoscaling**
    - Reproduce the [walkthrough](https://kubernetes.io/docs/user-guide/horizontal-pod-autoscaling/walkthrough/), add any additional details as needed. [#126](https://github.com/reactiveops/pentagon/pull/126)
- All additional (dashboard, heapster, etc.) resources (Deployments, etc.) in the `kube-system` namespace are defined, and have a uniform method of application.
    - `default/clusters/working/kubernetes`  and `default/clusters/production/kubernetes` are not identical, and probably need to moved out of `default/clusters/xxx`
    - one possibility would be `pentagon initialize-cluster $clustername` which would drop in `default/clusters/$clustername/kubernetes`  and then the next step would be `kubectl apply -f default/clusters/$clustername/kubernetes` [#29](https://github.com/reactiveops/pentagon/issues/29)
- **Centralized Logging**, minimally of kube-system logs, optionally all pods' logs to an EL/FK stack, via AWS ES, fluentd, and Kibana (likely in a Deployment with nginx, not AWS' default Kibana- enabling locking down via VPN) #14, #41
- Define the base set of IAM permissions
- Hosted, browsable docs (via `mkdocs`).

## [1.1](https://github.com/reactiveops/pentagon/milestone/3)
- **Improved Secrets Management** via something more structured than "Secrets are kept in S3" or "Secrets are kept in an encrypted vault (1password)." A very likely candidate is implementing Hashicorp Vault (free) for all clients by default, and optionally adding Pro for the clients that request it [#76](https://github.com/reactiveops/pentagon/issues/76)
- **Integration tests**: scripted tests that pass and fail as features and bugs are fixed
- **DNS integration with applications** (via wearemolecule/r53)
    - Just needs to be added to the addons in #29, IAM permissions, and documented
- Provable, testable **HA multi-master**: A master should be a member of a herd and not a cat [Pets vs. Cattle](https://www.slideshare.net/randybias/the-history-of-pets-vs-cattle-and-using-it-properly). In other words, a cluster should gracefully recover from a master outage in a multi-master setup. [#54](https://github.com/reactiveops/pentagon/issues/54)
    - Documented recovery procedures, research, pointers to relevant documentation- what should be known by us.
- **Documentation for the future of the pentagon CLI** tool: what should it do, what should it not do
    - A method for including "components"- ie. `pentagon install-component elasticsearch` should do foo and bar.
    - Add a design doc- list future planned features without necessarily coding them. For example, mimicking the kops `create/update` behavior
- **Docs for kubernetes upgrades via kops**, ie- the way it is done in Pentagon. Linking to docs and a human-scriptable test of current-1 to current.

## [1.2](https://github.com/reactiveops/pentagon/milestone/6)
- Pentagon
    - **Default $client-infra repos' docs** should include references to some basic AWS things, like the personal health dashboard, cloudwatch metrics, Budget configuration
    - **Every infrastructural resource built via pentagon should have a defined monitoring method**. infrastructure-side monitored. Meaning, if AWS ES is enabled, than that ES cluster should be monitored. Likewise all the `kube-system` resources, Vault, etc. The AWS personal health dashboard, or other alarms (cloudwatch perhaps) should be accessible as well, typically via Hydra
- Outside Pentagon
    - k8s-scripts should support CircleCI 2.0.
    - A defined set of pre-tasks for setting up applications how is a registry created?  Access defined?

## [1.3](https://github.com/reactiveops/pentagon/milestone/7)
- Pentagon
    - Everything doable in pentagon on AWS to this point should be doable in GCP
- Outside Pentagon
    - Expand the list of Supported CIs by k8s-scripts to include Jenkins, with a functional demo

## [1.4](https://github.com/reactiveops/pentagon/milestone/8)
- Investigate **Canary and other** [**deployment strategies**](https://kubernetes.io/docs/user-guide/deployments/#strategy)
    - canary deployments perhaps tied to app metrics
- Application Deployments to Ephemeral Environments
- **Deployment manager**. For example, airware/vili

## [1.5](https://github.com/reactiveops/pentagon/milestone/9)
- Outside Pentagon
    - Public Demo

## [1.6](https://github.com/reactiveops/pentagon/milestone/10)
- **CI inside the cluster via Drone or Jenkins**
    - Research needed: is this a good idea / is Drone mature enough.
- **Chatops**: A cluster user should be able to do some operations on their infrastructure via chat. Define those operations, and have a default implementation path.
- **Cluster Shell**
    - [PR on kubernetes/dashboard](https://github.com/kubernetes/dashboard/pull/1455) / [Issue](https://github.com/kubernetes/dashboard/issues/1345)

## [1.7](https://github.com/reactiveops/pentagon/milestone/11)
- **Metrics**
    - A default method for applications to push metrics, and for them to be viewed. Prometheus and Graphite are contenders here

---
