Pentagon is the way ReactiveOps does DevOps as a Service (DaaS).

It is our curated ecosystem of container-based infrastructure based on Kubernetes.


# Getting Started

## Requirements
* python >= 2.7
* pip install -e git+ssh://git@github.com/reactiveops/pentagon#egg=pentagon


## Usage
### QUICK START
* `pentagon start-project <project-name> --aws-access-key <aws-access-key> --aws-secret-key <aws-secret-key> --aws-default-region <aws-default-region>`
  * With the above basic options set, all defaults will be set for you and unless values need to be updated, you should be able to run terraform after creating the S3 Bucket to store state (`state-store-bucket`).

### Start new project
* `pentagon start-project <project-name> <options>`

### Clone existing project
* `pentagon start-project <project-name> --git-repo <repository-of-existing-project> <options>`

### Available commands
* `pentagon delete-project`
* `pentagon start-project`

### _start-project_

 `pentagon start-project` creates a new project in your workspace directory and creates a matching virutalenv for you. Most values have defaults that should get you up and running very quickly with a new pentagon project. You may also clone an existing pentagon project if one exists.

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
    * If the --aws-default-region option is set it will allow the default to be set for `--aws-availability-zones` and `--aws-availability-zone-count`
  * **--aws-availability-zone-count**
    * Number of availability zones to use
    * Defaults to 3 when a default region is entered. Otherwise, a placeholder string is used
  * **--aws-availability-zones**:
    * AWS availability zones as a comma delimited list.
    * Defaults to `<aws-default-region>a`, `<aws-default-region>b`, ... `<aws-default-region>z` when `--aws-default-region` is set calculated using the `--aws-available-zone-count` value. Otherwise, a placeholder string is used.
  * **--aws-availability-zone-count**:
    * Number of availability zones to use
    * Defaults to 3 when a default recion is entered. Otherwise, a placeholder string is used
  * **--state-store-bucket**:
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
    * ***Keys are not uploaded to AWS, when needed, this will need to be done manually***
  * **--admin-vpn-key**:
    * Name of the ssh key for the admin user of the VPN instance
    * Defaults to 'admin_vpn'
  * **--working-kube-key**:
    * Name of the ssh key for the working kubernetes cluster
    * Defaults to 'working_kube'
  * **--production-kube-key**:
    * Name of the ssh key for the production kubernetes cluster
    * Defaults to 'production_kube'
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
    * AWS instance type of the kube workder nodes in the production cluster
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
  * **--log-level**:
    * Log Level. Accepts DEBUG,INFO,WARN,ERROR
    * Defaults to INFO
  * **--help**:
    * Show help message and exit.
### _delete-project_

`pentagon delete-project <project-name>` removes the project directory in your workspace and the matching virtualenv of the same name. ***Use with caution, there is no confirmation prompt.***
#### Options
  * **--workspace-directory**:
   * Directory to place new project
   * Defaults to `~/workspace/`
  * **--log-level**:
    * Log Level. Accepts DEBUG,INFO,WARN,ERROR
    * Defaults to INFO
  * **--help**:
    * Show help message and exit.

## Example
* The following command shows the minimal argumets to creat a project without any extra configuration. Without aws-default-region, aws-secret-key, aws-access-key further configuration is required.
    * `pentagon start-project test --log-level DEBUG  --aws-default-region us-west-2 --aws-secret-key=<aws-secret-key> --aws-access-key=<aws-access-key>`

When this is successful, the directory structure will look like this:
```    
.
└── test-infrastructure
    ├── README.md
    ├── ansible-requirements.yml
    ├── config
    │   ├── local
    │   │   ├── ansible.cfg
    │   │   ├── local-config-init
    │   │   ├── ssh_config
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
    │   │   │   │   ├── elk.yaml
    │   │   │   │   ├── namespaces.yml
    │   │   │   │   └── readme.md
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
