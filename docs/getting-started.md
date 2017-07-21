Pentagon is the way ReactiveOps does DevOps as a Service (DaaS).

It is our curated ecosystem of container-based infrastructure based on Kubernetes.


# Getting Started

## Requirements
* python >= 2.7
* pip install -e git+ssh://git@github.com/reactiveops/pentagon#egg=pentagon
* [terraform 0.8.8](https://releases.hashicorp.com/terraform/0.8.8/)

## Usage
### QUICK START
* `pentagon start-project <project-name> --aws-access-key <aws-access-key> --aws-secret-key <aws-secret-key> --aws-default-region <aws-default-region>`
  * With the above basic options set, all defaults will be set for you and unless values need to be updated, you should be able to run terraform after creating the S3 Bucket to store state (`infrastructure-bucket`).
  * You may set

### Start new project
* `pentagon start-project <project-name> <options>`

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
    * Defaults to `~/workspace/`
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
  * **--vpn-ami-id
    * AWS ami id to use for the VPN instance
    * Defaults to looking up ami-id from AWS
  * **--log-level**:
    * Pentagon CLI Log Level. Accepts DEBUG,INFO,WARN,ERROR
    * Defaults to INFO
  * **--help**:
    * Show help message and exit.

## Example Usage
* The following command shows the minimal arguments to create a project without any extra configuration. Without aws-default-region, aws-secret-key, aws-access-key further configuration is required.
    * `pentagon start-project test --log-level DEBUG  --aws-default-region us-west-2 --aws-secret-key=<aws-secret-key> --aws-access-key=<aws-access-key>`
* In action: (actual output is more verbose, truncated output indicated by "...")

```
$ mkproject testinit5
New python executable in /Users/myuser/Documents/work/reactive/workspace/venvs/testinit5/bin/python
...
(testinit5) 702 myuser:testinit5$ pip install -e ../reactiveops/pentagon/
Obtaining file:///Users/myuser/Documents/work/reactive/workspace/projects/reactiveops/pentagon
...
Successfully installed GitPython-2.1.3 Jinja2-2.9.5 MarkupSafe-1.0 PyYAML-3.12 click-6.7 gitdb2-2.0.0 pbr-2.0.0 pentagon pycrypto-2.6.1 six-1.10.0 smmap2-2.0.1 stevedore-1.21.0 virtualenv-15.1.0 virtualenv-clone-0.2.6 virtualenvwrapper-4.7.2
(testinit5) 705 myuser:testinit5$ pentagon start-project hillghost1 --aws-access-key PPP --aws-secret-key QQQ --aws-default-region us-east-1
INFO:root:Creating default AWS AZs
...

# S3 buckets will need to be created

# Execute the following steps to create VPC
workon <project_name>
cd <project_name>-infrastructure/default/vpc
source ../account/vars.sh
make plan
make apply

# VPN still requires configuration

# Get VPCID and add it to default/clusters/<production|working>/vars.sh before running default/clusters/<production|working>/cluster-config/kops.sh

(testinit5) 706 myuser:testinit5$ workon hillghost1
(hillghost1) 707 myuser:hillghost1$ ls
hillghost1-infrastructure
(hillghost1) 710 myuser:hillghost1$ echo $AWS_ACCESS_KEY
PPP
(hillghost1) 711 myuser:hillghost1$ echo $ANSIBLE_CONFIG
/Users/myuser/Documents/work/reactive/workspace/projects/hillghost1/hillghost1-infrastructure/config/local/ansible.cfg
```

* When this is successful, the directory structure will look like this:
```
(hillghost1) 708 myuser:hillghost1$ tree
.
└── hillghost1-infrastructure
    ├── README.md
    ├── ansible-requirements.yml
    ├── config
    │   ├── local
    │   │   ├── ansible.cfg-default
    │   │   ├── local-config-init
    │   │   ├── ssh_config-default
    │   │   └── vars -> ../private/vars
    │   ├── private
    │   │   ├── admin-vpn
    │   │   ├── admin-vpn.pub
    │   │   ├── production-kube
    │   │   ├── production-kube.pub
    │   │   ├── production-private
    │   │   ├── production-private.pub
    │   │   ├── vars
    │   │   ├── working-kube
    │   │   ├── working-kube.pub
    │   │   ├── working-private
    │   │   └── working-private.pub
    │   └── requirements.txt
    ├── default
    │   ├── account
    │   │   ├── vars.sh
    │   │   └── vars.yml
    │   ├── clusters
    │   │   ├── production
    │   │   │   ├── cluster-config
    │   │   │   │   └── kops.sh
    │   │   │   ├── kubernetes
    │   │   │   │   ├── docker-gc-configmap.yml
    │   │   │   │   ├── docker-gc.yml
    │   │   │   │   ├── elk.yaml
    │   │   │   │   ├── es-curator-config.yml
    │   │   │   │   ├── es-curator.yml
    │   │   │   │   ├── namespaces.yml
    │   │   │   │   ├── readme.md
    │   │   │   │   ├── route53-kubernetes.example.service.yml
    │   │   │   │   ├── route53-kubernetes.policy
    │   │   │   │   └── route53-kubernetes.yml
    │   │   │   ├── resources
    │   │   │   │   └── readme.md
    │   │   │   └── vars.sh
    │   │   └── working
    │   │       ├── cluster-config
    │   │       │   └── kops.sh
    │   │       ├── kubernetes
    │   │       │   ├── namespaces.yml
    │   │       │   └── readme.md
    │   │       ├── resources
    │   │       │   └── readme.md
    │   │       └── vars.sh
    │   ├── resources
    │   │   ├── admin-environment
    │   │   │   ├── env.yml
    │   │   │   └── vpn.yml
    │   │   └── readme.md
    │   └── vpc
    │       ├── Makefile
    │       ├── main.tf
    │       ├── terraform-remote.sh
    │       ├── terraform.tfvars
    │       └── variables.tf
    ├── docs
    │   └── readme.md
    ├── plugins
    │   ├── filter_plugins
    │   │   └── flatten.py
    │   └── inventory
    │       ├── base
    │       ├── ec2.ini
    │       └── ec2.py
    └── roles
```
