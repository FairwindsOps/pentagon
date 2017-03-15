Pentagon is the way ReactiveOps does DevOps as a Service (DaaS).

It is our curated ecosystem of container-based infrastructure based on Kubernetes.


# Getting Started

Commands:
  configure-project
  delete-project
  start-project

```

```
# pentagon start-project --help
Usage: pentagon start-project [OPTIONS] NAME

Options:
  --workspace-directory TEXT      Directory to place new project, defaults to
                                  ~/workspace/
  --repository-name TEXT          Name of the folder to initialize the
                                  infrastructure repository
  --configure / --no-configure    Configure project with default settings
  --force / --no-force            Ignore existing directories and copy project
  --aws-access-key TEXT           AWS access key
  --aws-secret-key TEXT           AWS secret key
  --aws-default-region TEXT       AWS default region
  --aws-availability-zones TEXT   AWS availability zones as a comma delimited
                                  with spaces. Default to region a, region b,
                                  ... region z
  --aws-availability-zone-count TEXT
                                  Number of availability zones to use
  --state-store-bucket TEXT       Name of S3 Bucket to store state
  --git-repo TEXT                 Existing git repository to clone
  --create-keys / --no-create-keys
                                  Ignore existing directories and copy project
  --admin-vpn-key TEXT            Name of the ssh key for the admin user of
                                  the VPN instance
  --working-kube-key TEXT         Name of the ssh key for the working
                                  kubernetes cluster
  --production-kube-key TEXT      Name of the ssh key for the production
                                  kubernetes cluster
  --working-private-key TEXT      Name of the ssh key for the working non
                                  kubernetes instances
  --production-private-key TEXT   Name of the ssh key for the production non
                                  kubernetes instances
  --vpc-name TEXT                 Name of VPC to create
  --vpc-cidr-base TEXT            First two octets of the VPC ip space
  --log-level TEXT                Log Level DEBUG,INFO,WARN,ERROR
  --help                          Show this message and exit.
```
```
# pentagon configure-project --help
Usage: pentagon configure-project [OPTIONS] NAME

Options:
  --workspace-directory TEXT      Directory to place new project, defaults to
                                  ~/workspace/
  --repository-name TEXT          Name of the folder to initialize the
                                  infrastructure repository
  --aws-access-key TEXT           AWS access key
  --aws-secret-key TEXT           AWS secret key
  --aws-default-region TEXT       AWS default region
  --aws-availability-zones TEXT   AWS availability zones as a comma delimited
                                  with spacesDefault to region a, region b,
                                  ... region z
  --aws-availability-zone-count TEXT
                                  Number of availability zones to use
  --state-store-bucket TEXT       Name of S3 Bucket to store state
  --git-repo TEXT                 Existing git repository to clone
  --create-keys / --no-create-keys
                                  Ignore existing directories and copy project
  --admin-vpn-key TEXT            Name of the ssh key for the admin user of
                                  the VPN instance
  --working-kube-key TEXT         Name of the ssh key for the working
                                  kubernetes cluster
  --production-kube-key TEXT      Name of the ssh key for the production
                                  kubernetes cluster
  --working-private-key TEXT      Name of the ssh key for the working non
                                  kubernetes instances
  --production-private-key TEXT   Name of the ssh key for the production non
                                  kubernetes instances
  --vpc-name TEXT                 Name of VPC to create
  --vpc-cidr-base TEXT            First two octets of the VPC ip space
  --log-level TEXT                Log Level DEBUG,INFO,WARN,ERROR
  --help                          Show this message and exit.
```
```
# pentagon delete-project --help
Usage: pentagon delete-project [OPTIONS] NAME

Options:
  --workspace-directory TEXT  Directory to place new project, defaults to
                              ~/workspace/
  --log-level TEXT            Log Level DEBUG,INFO,WARN,ERROR
  --help                      Show this message and exit.
```


## Example
* The following command shows the minimal argumets to creat a project without any extra configuration. Without aws-default-region, aws-secret-key, aws-access-key further configuration is required.
    * `pentagon start-project test --log-level DEBUG  --aws-default-region us-west-2 --aws-secret-key=<aws-secret-key> --aws-access-key=<aws-access-key>`

When this is successful, the directory structure will look like this:
```    
$ tree test
test
├── README.md
├── ansible-requirements.yml
├── config
│   ├── local
│   │   ├── ssh_config
│   │   ├── vars -> ../private/vars
│   │   └── vars-private.example
│   ├── private
│   └── requirements.txt
├── default
│   ├── account
│   │   └── vars.sh
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
│   │   │   ├── vars.sh
│   │   │   └── vars.sh.example
│   │   └── working
│   │       ├── cluster-config
│   │       │   └── kops.sh
│   │       ├── kubernetes
│   │       │   ├── namespaces.yml
│   │       │   └── readme.md
│   │       ├── resources
│   │       │   └── readme.md
│   │       ├── vars.sh
│   │       └── vars.sh.example
│   ├── resources
│   │   ├── all.yml
│   │   ├── env.yml
│   │   ├── environment.yml
│   │   ├── first_run.yml
│   │   ├── readme.md
│   │   └── vpn
│   │       └── stack.yml
│   └── vpc
│       ├── Makefile
│       ├── main.tf
│       ├── terraform-remote.sh
│       ├── terraform.tfvars
│       ├── terraform.tfvars.example
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
22 directories, 37 files
```

Next, take a look at the [kops instructions](kops.md).
