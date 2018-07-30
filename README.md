# Pentagon

## What is Pentagon?

**Pentagon is a cli tool to generate repeatable, cloud-based [Kubernetes](https://kubernetes.io/) infrastructure**
It is “batteries included”- not only does one get a network with a cluster, but the defaults include these commonly desired features:
- At the core, powered by Kubernetes. Configured to be highly-available: masters and nodes are clustered
- Segregated multiple development / non-production environments
- VPN-based access control
- A highly-available network, built across multiple Availability Zones

## How does it work?
 **Pentagon produces a directory.** The directory defines a basic set of configurations for [Ansible](https://www.ansible.com/), [Terraform](https://www.terraform.io/) and [kops](https://github.com/kubernetes/kops)). When those tools are run in a specific order the result is a VPC with a VPN and a Kubernetes Cluster in AWS. (GKE Support is in the works). It is designed to be customizable while at the same time built with defaults that fit the needs of most web application companies.

Take a look at [Getting Started](https://reactiveops.github.io/pentagon/getting-started.html) to begin.

[![CLA assistant](https://cla-assistant.io/readme/badge/reactiveops/pentagon)](https://cla-assistant.io/reactiveops/pentagon)
