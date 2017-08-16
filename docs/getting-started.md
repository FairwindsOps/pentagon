# Getting Started with Pentagon

## Requirements
* python2 >= 2.7 [Install Python](https://www.python.org/downloads/)
* pip [Install Pip](https://pip.pypa.io/en/stable/installing/)
* git [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* Terraform >=0.9 [Install Terraform ](https://www.terraform.io/downloads.html)
* Ansible [Install Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html)
* Kubectl [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* Kops [Install Kops](https://github.com/kubernetes/kops#installing)

## Installation
* `pip install -e git+https://github.com/reactiveops/pentagon.git#egg=pentagon`
  * the `-e` is important to include. The next steps will fail without it.
  * May require the `python-dev` and `libffi-dev` packages on some linux distributions
  * Not necessary, but we suggest installing Pentagon into a [VirtualEnv](https://virtualenv.pypa.io/en/stable/)

## Quick Start
### Create a pentagon project
* `pentagon start-project <project-name> --aws-access-key <aws-access-key> --aws-secret-key <aws-secret-key> --aws-default-region <aws-default-region>`
  * With the above basic options set, all defaults will be set for you and unless values need to be updated, you should be able to run terraform after creating the S3 Bucket to store state (`infrastructure-bucket`).
  * Arguments may also be set using environment variable in the format `PENTAGON_<argument_name_with_underscores>`.
* `cd <project-name>-infrastructure`
* `pip install -r requirements.txt`
* `source config/local/env-vars.sh`
  * sources environment variables required for the further steps. This wil be required each time you work with the infrastructure repository or if you move the repository to another location.
* `bash config/local/local-config-init`

### Create a VPC
This creates a VPC and private, public, and admin subnets in that VPC for non Kubernetes resources. Read more about networking [here](network.md).
* `cd default/vpc`
* Edit `terraform.tfvars`and verify the generated `aws_azs` actually exist in `aws_region`
* `make all`
* In `default/clusters/*/vars.sh`, set `VPC_ID` using the newly created VPC ID. You can find that ID in Terraform output or using the AWS web console.

### Configure DNS and Route53
If you don't already have a Route53 Hosted Zone configured, do that now.
* Create a Route53 Hosted Zone (e.g. `pentagon.mycompany.com`)
* In `default/account/vars.yml` set `canonical_zone` to match your Hosted Zone
* In `default/clusters/*/vars.sh`
  * Set `CLUSTER_NAME` to a hostname that ends with your hosted zone (e.g. `working-1.pentagon.mycompany.com`)
  * Set `DNS_ZONE` to your Hosted Zone (e.g. `pentagon.mycompany.com`)

### Setup a VPN
This creates a AWS instance running [OpenVPN](https://openvpn.net/). Read more about the VPN [here](vpn.md).
* From the root of your project run `ansible-galaxy install -r ansible-requirements.yml`
* `cd default/resources/admin-environment`
* In `env.yml`, set the list of user names that should have access to the VPN under `openvpn_clients`. You can add more later.
* Run Ansible a few times
  * Run `ansible-playbook vpn.yml` until it fails on `VPN security groups`
  * Run `ansible-playbook vpn.yml` until it fails `Gathering Facts` after you agree to trust the SSH key for the host.
  * Run `ansible-playbook vpn.yml` one last time and it will succeed.
  * Edit `config/private/ssh_config` and add the IP address from the SSH key prompt to the `#VPN instance` section.

### Create a Kubernetes cluster
Pentagon used Kops to create clusters in AWS. The default layout creates configurations for two kubernetes clusters: `working` and `production`. See [Overview](overview.md) for a more comprehensive description of the directory layout.

* Make sure your KOPS variables are set correctly with `source default/account/vars.sh`
* Move into to the path for the cluster you want to work on with `cd default/clusters/<production|working>`
* Run `bash cluster-config/kops.sh` to create a cluster.spec file for this cluster. This does not create any resources in AWS.
* Use [kops](https://github.com/kubernetes/kops/blob/master/docs/cli/kops.md) to manage the cluster.
  * Run `kops edit cluster <clustername>` to view and edit the `cluster.spec` and make the following edits
    * Choose approriate CIDR ranges for your Kubernetes subnets. That don't conflict with the subnets that were created in the [VPC](#vpc-setup) step. We typically reccomend fairly small subnets ie /22 or /24.
    * Using the AWS console, find the `NAT Gateways` section of the `VPC Dashboard`. Note the `NAT Gateway ID`s for each of your AZs. For each of the `Private` subnets in the `cluster.spec` add an `egress: <nat-id>` line where `nat-id` is the `NAT Gateway ID` corresponding to the same AZ as the `Private` subnet.
    * Save and exit
  * You may also wish to edit the instance groups prior to cluster creation:
    * `kops get instancegroups --name <clustername>` to list them (one master group per AZ and one node group)
    * `kops edit instancegroups --name <clustername> <instancegroupname>` to edit any of them
* Run `kops update cluster <clustername>` and review the out put to ensure it matches the cluster you wish to create
* Run `kops update cluster <clustername> --yes` to create the cluster
* While waiting for the cluster to create, consult the [kops documentation](https://github.com/kubernetes/kops/blob/master/docs/README.md) for more information about using kops and interacting with your new cluster

### Creating resources outside of Kubernetes

Typically infrastructure will be required outside of your Kubernetes cluster. Other EC2 isntances or RDS instance or Elasticache instances etc are often require for an application.

The directory structure of the project suggests that you use Ansible to create these resources and that the ansible playbooks can be save in the `default/resources/` direcotry or the `default/clusters/<cluster>/resoures/` directory depending on the scope the play book will be utilized. If the resoures is not specific to either cluster, then we suggest you save it at the `deault/resources/` level. Likewise, if it is a resources that will only be used by one cluster, such as a staging database or a production database, then we suggest writing the Ansible playbook at the `default/cluster/<cluster>/resources/` level. Writing ansible roles can be very helpful to DRY up your resource configurations.


======================================

## Advanced Project Initialization

If you wish to utilize the templating ability of the `pentagon start-project` command, but need to modify the defaults, a comprehensive list of command line flags, listed below, should be able to customize the outout of the `pentagon start-project` command to your liking.


### Start new project
* `pentagon start-project <project-name> <options>`
  * This will create a skeleton repository with placeholder strings in place of the options shown above in the [QUICK START]
  * Edit the `config/private/secrets.yml` and `config/local/env.yml` before proceeding onto the next step

### Clone existing project
* `pentagon start-project <project-name> --git-repo <repository-of-existing-project> <options>`

### Available commands
* `pentagon start-project`

### _start-project_

 `pentagon start-project` creates a new project in your workspace directory and creates a matching virtualenv for you. Most values have defaults that should get you up and running very quickly with a new pentagon project. You may also clone an existing pentagon project if one exists.  You may set any of these options as environment variables instead by prefixing them with `PENTAGON_`, for example, for security purposes `PENTAGON_aws_access_key` can be used instead of `--aws-access-key`

 #### Options
  * **-f, --config-file**:
    * File to read configuration options from.
    * No default
    * ***File supercedes command line options.***
  * **-o, --output-file**:
    * No default
  * **--workspace-directory**:
    * Directory to place new project
    * Defaults to `./`
  * **--repository-name**:
    * Name of the folder to initialize the infrastructure repository
    * Defaults to `<project-name>-infrastructure`
  * **--configure / --no-configure:**:
    * Configure project with default settings
    * Default to True
    * If you choose `--no-configure`, placeholder values will be used in stead of defaults and you will have to manually edit the configuration files
  * **--force / --no-force**:
    * Ignore existing directories and copy project anyway
    * Defaults to False
  * **--aws-access-key**:
    * AWS access key
    * No Default
  * **--aws-secret-key**:
    * AWS secret key
    * No Default
  * **--aws-default-region**:
    * AWS default region
    * No Default
    * If the `--aws-default-region` option is set it will allow the default to be set for `--aws-availability-zones` and `--aws-availability-zone-count`
  * **--aws-availability-zones**:
    * AWS availability zones as a comma delimited list.
    * Defaults to `<aws-default-region>a`, `<aws-default-region>b`, ... `<aws-default-region>z` when `--aws-default-region` is set calculated using the `--aws-available-zone-count` value. Otherwise, a placeholder string is used.
  * **--aws-availability-zone-count**:
    * Number of availability zones to use
    * Defaults to 3 when a default region is entered. Otherwise, a placeholder string is used
  * **--dns-zone**:
    * DNS Zone of the project. Used for VPN instance and Kubernetes api
    * Kubernetes dns zones can be overriden with arguments found below
    * Defaults to `<project-name>.com`
  * **--infrastructure-bucket**:
    * Name of S3 Bucket to store state
    * Defaults to `<project-name>-infrastructure`
    * pentagon start-project does not create this bucket and it will need to be created
  * **--git-repo**:
    * Existing git repository to clone
    * No Default
    * ***When --git-repo is set, no configuration actions are taken. Pentagon will setup the virutualenv and clone the repository only***
  * **--create-keys / --no-create-keys**:
    * Create ssh keys or not
    * Defaults to True
    * Keys are saved to `<workspace>/<repsitory-name>/config/private`
    * 5 keys will be created:
      * `admin_vpn`: key for the vpn instances
      * `working_kube`: key for working kubernetes instances
      * `production_kube`: key for production kubernetes instance
      * `working_private`: key for non-kubernetes resources in the working private subnets
      * `production_private`: key for non-kubernetes resources in the production private subnets
    * ***Keys are not uploaded to AWS. When needed, this will need to be done manually***
  * **--admin-vpn-key**:
    * Name of the ssh key for the admin user of the VPN instance
    * Defaults to 'admin_vpn'
  * **--working-kube-key**:
    * Name of the ssh key for the working kubernetes cluster
    * Defaults to 'working_kube'
  * **--production-kube-key**:
    * Name of the ssh key for the production kubernetes cluster
    * Defaults to 'production_kube'
  * **--working-private-key**:
    * Name of the ssh key for the working non-kubernetes instances
    * Defaults to 'working_private'
  * **--production-private-key**:
    * Name of the ssh key for the production non-kubernetes instances
    * Defaults to 'production_private'
  * **--vpc-name**:
    * Name of VPC to create
    * Defaults to date string in the format `<YYYYMMDD>`
  * **--vpc-cidr-base**
    * First two octets of the VPC ip space
    * Defaults to '172.20'
  * **--working-kubernetes-cluster-name**:
    * Name of the working kubernetes cluster nodes
    * Defaults to `working-1.<project-name>.com`
  * **--working-kubernetes-node-count**:
    * Number of the working kubernetes cluster nodes
    * Defaults to 3
  * **--working-kubernetes-master-aws-zone**:
    * Availability zone to place the kube master in
    * Defaults to the first zone in --aws-availability-zones
  * **--working-kubernetes-master-node-type**:
    * AWS instance type of the kube master node in the working cluster
    * Defaults to t2.medium
  * **--working-kubernetes-worker-node-type**:
    * AWS instance type of the kube worker nodes in the working cluster
    * Defaults to t2.medium
  * **--working-kubernetes-dns-zone**:
    * DNS Zone of the kubernetes working cluster
    * Defaults to `working.<project-name>.com`
  * **--working-kubernetes-v-log-level**:
    * V Log Level kubernetes working cluster
    * Defaults to 10
  * **--working-kubernetes-network-cidr**:
    * Network cidr of the kubernetes working cluster
    * Defaults to `172.20.0.0/16`
  * **--production-kubernetes-cluster-name**:
    * Name of the production kubernetes cluster nodes
    * Defaults to `production-1.<project-name>.com`
  * **--production-kubernetes-node-count**:
    * Number of the production kubernetes cluster nodes
    * Defaults to 3
  * **--production-kubernetes-master-aws-zone**:
    * Availability zone to place the kube master in
    * Defaults to the first zone in --aws-availability-zones
  * **--production-kubernetes-master-node-type**:
    * AWS instance type of the kube master node in the production cluster
    * Defaults to t2.medium
  * **--production-kubernetes-worker-node-type**:
    * AWS instance type of the kube worker nodes in the production cluster
    * Defaults to t2.medium
  * **--production-kubernetes-dns-zone**:
    * DNS Zone of the kubernetes production cluster
    * Defaults to `production.<project-name>.com`
  * **--production-kubernetes-v-log-level**:
    * V Log Level kubernetes production cluster
    * Defaults to 10
  * **--production-kubernetes-network-cidr**:
    * Network cidr of the kubernetes production cluster
    * Defaults to `172.20.0.0/16`
  * **--configure-vpn/--no-configure-vpn**:
    * Do, or do not configure the vpn env.yaml file
    * Defaults to True
  * **--vpn-ami-id**
    * AWS ami id to use for the VPN instance
    * Defaults to looking up ami-id from AWS
  * **--log-level**:
    * Pentagon CLI Log Level. Accepts DEBUG,INFO,WARN,ERROR
    * Defaults to INFO
  * **--help**:
    * Show help message and exit.
