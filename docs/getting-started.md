Pentagon is the way ReactiveOps does DevOps as a Service (DaaS).

It is our curated ecosystem of container-based infrastructure based on Kubernetes.

# Getting Started

* Clone the pentagon repo to a location on your workstation. Do not put it into a python project directory structure (such as the omnia workspace).
* Here are the basic instructions on setting up a pentagon project for the first time. It assumes that you have virtualenvwrapper setup as described [here](virtualenv.md).

* `mkproject delme`
* `pip install -e git+ssh://git@github.com/reactiveops/pentagon#egg=pentagon`
* `pentagon-startproject -n delme`

When this is successful, the directory structure will look like this:
```    
$ tree delme
delme
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

# Setting up your configuration files and credentials

* Customize `config/local/ansible.cfg` and `config/local/ssh_config`


Next, take a look at the [kops instructions](kops.md).
