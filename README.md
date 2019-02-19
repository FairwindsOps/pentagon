# Pentagon

## What is Pentagon?

**Pentagon is a cli tool to generate repeatable, cloud-based [Kubernetes](https://kubernetes.io/) infrastructure.**
It can be used as a “batteries included” default which can:
- provide a network with a cluster
- Two HA KOPS based Kubernetes clusters
- Segregated multiple development / non-production environments
- VPN-based access control
- A highly-available network, built across multiple Availability Zones

## How does it work?
 **Pentagon produces a directory.** The directory defines a basic set of configurations for [Ansible](https://www.ansible.com/), [Terraform](https://www.terraform.io/) and [kops](https://github.com/kubernetes/kops)). When those tools are run in a specific order the result is a VPC with a VPN and a Kubernetes Cluster in AWS. GKE Support is built in but not default. It is designed to be customizable while at the same time built with defaults that fit the needs of most web application companies.


## Getting Started

The [Getting Started](docs/getting-started.md) has information about installing Pentagon and creating your first project.

Table Of Contents
=================

* [Requirements](docs/getting-started.md#requirements)
* [Installation](docs/getting-started.md#installation)
* [Quick Start Guide](docs/getting-started.md)
  * [VPC](docs/getting-started.md#vpc-setup)
  * [VPN](docs/getting-started.md#vpn-setup)
  * [KOPS](docs/getting-started.md#kops)
* [Advanced Usage](docs/getting-started.md#advanced-project-initialization)
* [Infrastrucure Repository Overview](docs/overview.md)
* [Component](docs/components.md)


## AWS Virtual Private Cloud

A VPC configuration is provided with Terraform. Details can be found on the [VPC Setup Page](docs/vpc.md).

## Virtual Private Network

Configuration is provided for an OpenVPN setup in the VPC. Details can be found on the [VPN Setup Page](docs/vpn.md).



[![CLA assistant](https://cla-assistant.io/readme/badge/reactiveops/pentagon)](https://cla-assistant.io/reactiveops/pentagon)
