# Pentagon Components

The functionality of Pentagon can be extended with components. Currently only two commands are accepted `add` and `get`. Data is passed to the compenent in `Key=Value` pairs and `-D` flag or from a datafile in yml or json format. For some components, environment variables may also be used. See documentation for the particular component.

Global options for both `get` and `add` component commands:

```
Usage: pentagon [add|get] [OPTIONS] COMPONENT_PATH [ADDITIONAL_ARGS]...

Options:
  -D, --data TEXT   Individual Key=Value pairs used by the component
  -f, --file TEXT   File to read Key=Value pair from (yaml or json are
                    supported)
  -o, --out TEXT    Path to output module result, if any
  --log-level TEXT  Log Level DEBUG,INFO,WARN,ERROR
  --help            Show this message and exit.
```

## Built in components

### gcp.cluster

- add: 
    - Creates `./<cluster_name>/create_cluster.sh` compiled from the data passed in.
    - `bash ./<cluster_name>/create_cluster.sh` will create the cluster as configured.
    - Argument keys are lower case, underscore separated version of the [gcloud container cluster create](https://cloud.google.com/sdk/gcloud/reference/beta/container/clusters/create) command.
    - If a `-f` file is passed in, data are merged with `-D` values ovveriding the file values.
    - Example: 
        ```
        pentagon add gcp.cluster -D name="pentagon-1" -D project="pentagon" -D zone="us-central1-a" -D additional_zones="us-central1-b,us-central1-b" -D network="pentagon" -o ./pentagon
        ```

- get: 
    - Creates `./<cluster_name>/create_cluster.sh` by querying the state of an existing cluster and parsing values. For when you have an existing cluster that you want to capture its configuration.
    - Creates `./<cluster_name>/node_pools/<node_pool_name>/create_nodepool.sh` for any nodepools that are not named `default-pool`. Set `-D get_default_nodepools=true` to capture configuration of `default-pool`. This is typically unecessary as the `create_cluster.sh` will already contain the configuration of the `default-pool`
    - `bash ./<cluster_name>/create_cluster.sh` will result in an error indicating the cluster is already present.
    - Argument keys are lower case, underscore separated version of the [gcloud container cluster describe](https://cloud.google.com/sdk/gcloud/reference/beta/container/node-pools/describe) command.
    - If `-f` file is passed in, data are merged with `-D` values ovveriding the file values
    - If `cluster` is omitted it will act on all clusters in the project
    - Example: 
      ```
      pentagon get gcp.cluster -D project="pentagon" -D zone="us-central1-a -D cluster="pentagon-1" -D get_default_nodepool="true"
      ```

### gcp.nodepool

- add:
    - Creates `./<nodepool_name>/create_nodepool.sh` compiled from the data passed in.
    - `bash ./<nodepool_name>/create_nodepool.sh` will create the nodepool as configured
    - Argument keys are lower case, underscore separated version of the [gcloud container node-pools create](https://cloud.google.com/sdk/gcloud/reference/beta/container/node-pools/create) command
    - If a `-f` file is passed in, data are merged with `-D` values ovveriding the file values
    - Example: 
      ```
      pentagon add gcp.nodepool -D name="pentagon-1-nodepool" -D project="pentagon" -D zone="us-central1-a" -D additional_zones="us-central1-b,us-central1-b" -D machine_type="n1-standard-64" --enable-autoscaling
      ```

- get: 
    - Creates `./<nodepool_name>/create_nodepool.sh` by querying the state of an existing cluster nodepool and parsing values. For when you have an existing cluster that you want to capture its configuration.
    - Creates `./<nodepool_name>/create_nodepool.sh` 
    - `bash ./<nodepool_name>/create_nodepool.sh` will result in an error indicating the cluster is already present.
    - Argument keys are lower case, underscore separated version of the [gcloud container node-pools describe](https://cloud.google.com/sdk/gcloud/reference/beta/container/node-pools/describe) command
    - If a `-f` file is passed in, data are merged with `-D` values ovveriding the file values
    - If `name` is omitted it will act on all nodepool in the cluster
    - Example:
        ```
        pentagon get gcp.nodepool -D project="pentagon" -D zone="us-central1-a -D cluster="pentagon-1" -D name="pentagon-1-nodepool"
        ```


### vpc

- add: 
    - Creates `./vpc/` directory with Terraform code for the Pentagon default AWS VPC described [here](#network).
    - `cd ./vpc; make all` will create the vpc as describe by the arguments passed in
    - In the normal course of using Pentagon and the infrastructure repository, it is unlikely you'll use this component as it is automatically installed by default.
    - Arguments:
        - vpc_name
        - vpc_cidr_base
        - aws_availabilty_zones
        - aws_availability_zone_count
        - aws_region
        - infrastructure_bucket
    - Without the arguments above, the `add` will complete but the output will be missing values required to create the VPC. You must edit the output files to add those values before it will function properly
    - Example:
        ```
        pentagon add vpc -D vpc_name="pentagon-vpc" -D vpc_cidr_base="172.20" -D aws_availability_zones="ap-northeast-1a, ap-northeast-1c" -D aws_availability_zone_count = "2" -D aws_region = "ap-northeast-1"
        ```
        
### kops.cluster

- add: 
    - Creates yml files in  `./<cluster_name>/` compiled from the data passed in.
    - `bash ./<cluster_name>/kops.sh` will create the cluster as configured.
    - Argument/ ConfigFile keys:
      - `additional_policies`: Additional IAM policies to inflict upon the cluster
      - `vpc_id`: AWS VPC Id of VPC to create cluster in (required)
      - `cluster_name`: Name of the cluster to create (required)
      - `kops_state_store_bucket`: Name of the s3 bucket where Kops State will be stored (required)
      - `cluster_dns`: DNS domain for cluster records (required)
      - `master_availability_zones`:  List of AWS Availability zones to place masters (required)
      - `availability_zones`:  List of AWS Availability zones to place nodes (required)
      - `kubernetes_version`: Version of Kubernetes Kops will install (required)
      - `nat_gateways`: List of AWS ids of the nat-gateways the Private Kops subnets will use as egress. Must be in the same order as the `availability_zones` from above. (required)
      - `master_node_type`: AWS instance type the masters should be (required)
      - `worker_node_type`: AWS instance type the default node group should be (required)
      - `ig_max_size`: Max number of instance in the default node group. (default: 3)
      - `ig_min_size`: Min number of instance in the default node group. (default: 3)
      - `ssh_key_path`: Path of public key for ssh access to nodes. (required)
      - `network_cidr`: VPC cidr for Kops created Kubernetes subnetes (default: 172.0.0.0/16)
      - `network_cidr_base`: First two octects of the network to template subnet cidrs from  (default: 172.0)
      - `third_octet`: Starting value for the third octet of the subnet cidrs (default: 16) 
      - `network_mask`: Value for network mask in subnet cidrs (defalt: 24)
      - `third_octet_increment`: Increment to increase third octet by for each of the Kubernetes subnets (default: 1) By default, the cidr of the first three private subnets will be 172.20.16.0/24, 172.20.17.0/24, 172.20.18.0/24
      - `authorization`: Authorization type for cluster. Allowed values are `alwaysAllow` and `rbac` (default: alwaysAllow)
    - Example Config File
    ```
    availability_zones: [eu-west-1a, eu-west-1b, eu-west-1c]
    additional_policies: |
      {
          "Effect": "Allow",
          "Action": [
              "autoscaling:DescribeAutoScalingGroups",
              "autoscaling:DescribeAutoScalingInstances",
              "autoscaling:DescribeTags",
              "autoscaling:SetDesiredCapacity",
              "autoscaling:TerminateInstanceInAutoScalingGroup"
          ],
          "Resource": "*"
      }
    cluster_dns: cluster1.reactiveops.io
    cluster_name: working-1.cluster1.reactiveops.io
    ig_max_size: 3
    ig_min_size: 3
    kops_state_store_bucket: reactiveops.io-infrastructure
    kubernetes_version: 1.5.7
    master_availability_zones: [eu-west-1a, eu-west-1b, eu-west-1c]
    master_node_type: t2.medium
    node_type: t2.medium
    ssh_key_path: ${INFRASTRUCTURE_REPO}/config/private//working-kube.pub
    vpc_id: vpc-4aa3fa2d
    network_cidr: 172.0.0.0/16
    network_cidr_base: 172.0
    third_octet: 16
    third_octet_increment: 1
    network_mask: 24
    nat_gateways:
      - nat-0c6ef9261d8ebd788
      - nat-0de4ec4c946e3b7ce
      - nat-08806276217bae9b5

    ```
    - If a `-f` file is passed in, data are merged with `-D` values overiding the file values.
    - Example: 
        ```
        pentagon add kops.cluster -f `pwd`/vars.yml --log-level=DEBUG
        ```

- get: 
    - Creates yml files in `./<cluster_name>/create_cluster.sh` by querying the state of an existing cluster and parsing values. For when you have an existing cluster that you want to capture its configuration.
    - Creates `./<cluster_name>/cluster.yml`, `./<cluster_name>/nodes.yml`, `./<cluster_name>/master.yml`, `./<cluster_name>/secret.sh`
    - `secret.sh` does not have the content of the secret and will be able re-create the cluster secret if needed. You will have to transform the key id into a saved public key.
    - Arguments:
      - `name`: Kops cluster name you are getting (required). Argument can also be set through and environment variable called "CLUSTER_NAME".
      - `kops_state_store_bucket`: s3 bucket name where cluster state is stored (required). Argument can also be set through and environment variable called "KOPS_STATE_STORE_BUCKET"
    - Example: 
      ```
      pentagon get kops.cluster -Dname=working-1.cluster.reactiveops.io -Dkops_state_store=reactiveops.io-infrastructure
      ```

### inventory
- add:
    - Creates account configuration directory. Creates all necessary files in `config`, `clusters` and `resources`. Depending on `type` it may also add a `vpc` component and `vpn` component under `resources`. Creates `clusters` directory but does not create cluster configuration. Use the cluster component for that.
    - `bash ./<nodepool_name>/create_nodepool.sh` will create the nodepool as configured
    - Arguments:
      - `name`: name of account to add to inventory
      - `type`: type of account to add to inventory aws or gcp (required). 
    - If a `-f` file is passed in, data are merged with `-D` values ovveriding the file values
    


## Writing your own components

Component modules must be named `pentagon<component_name>`. Classes are subclasses of the `pentagon.component.ComponentBase` class and they must be named <Component> (note the capital first letter).  The `pentagon add <component_name>` command will prefer built in components to external components so ensure your component name is not already in use. The <component_name> argument can be a dot separated module path ie `gcp.cluster` where the last parameter is the lowercase class name. For example. `gcp.cluster` finds the Cluster class in the cluster module in the gcp module.

Examples of plugin component package module name and use:
- pentagon_examplecomponent:
    *  package name: `pentagon-example-component`
    *  command: `pentagon add component`
    *  module path: `pentagon_component`
    *  class: `Component()`
- pentagon_kops
    *  package name: `pentagon-kops`
    *  command: `pentagon add kops`
    *  module path: `pentagon_kops`
    *  class: `Kops()`
- pentagon_kops.cluster
    *  package name: `pentagon-kops`
    *  command: `pentagon add kops.cluster`
    *  module path:  `pentagon_kops.kops`
    *  class: `Cluster()`
    

See [example](/example-component) 


