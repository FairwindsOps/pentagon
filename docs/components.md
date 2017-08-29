# Pentagon Components

The functionality of Pentagon can be extended with components. Currently only two commands are accepted `add` and `get`. Data is passed to the compenent in `Key=Value` pairs and `-D` flag or from a datafile in yml or json format.

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
    - In the normal course of using Pentagon and the infrastructure repository, it is unlikely you'll use this component.
    - Required Arguments:
        - vpc_name
        - vpc_cidr_base
        - aws_availabilty_zones
        - aws_availability_zone_count
        - aws_region
        - infrastructure_bucket
    - Example:
        ```
        pentagon add vpc -D vpc_name="pentagon-vpc" -D vpc_cidr_base="172.20" -D aws_availability_zones="ap-northeast-1a, ap-northeast-1c" -D aws_availability_zone_count = "2" -D aws_region = "ap-northeast-1"
        ```
        
## Writing your own components

Component modules must be named `pentagon<component_name>`. Classes are subclasses of the `pentagon.component.ComponentBase` class and they must be named <Component> (note the capital first letter).  The `pentagon add <component_name>` command will prefer built in components to extrenal components so ensure your component name is not already in use. The <component_name> argument can be a dot separated module path ie `gcp.cluster` where the last parameter is the lowercase class name. For example. `gcp.cluster` finds the Cluster class in the cluster module in the gcp module.

See [example](/example-component) 


