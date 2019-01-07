from copy import deepcopy


from pentagon import migration
from pentagon.migration import *
import yaml

ig_message = """
# This file has been updated to contain a new set of InstanceGroups with one per Subnet
# The min/max size should be the original size divided by the number of subnets
# In order to put the new InstanceGroups into service you will need to:
# 1. Ensure that the Min/Max size values are reasonable and double check the specs
# 2. `kops replace -f` this file
# 3. `kops update --yes` this cluster
# 4. ensure the InstanceGroups come up properly
# 5. cordon and drain the old nodes
# 6. Update the ClusterAutoScaler configuration. You should take this opportunity to
#    make it auto discover if appropriate: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md#auto-discovery-setup
# 7. `kops delete` the old, multi-subnet InstanceGroup and delete it from this file
# 8. Delete this comment and check the whole shebang into Git
# 9. Go engage in the relaxing activity of your choice

"""

readme = """

# Migration 2.6.2 -> 2.7.1

## This migration:
- removes older artifacts like the `post-kops.sh` if they exist
- renames `inventory/<inventory>/clusters/<cluster>/cluster` -> `inventory/<inventory>/clusters/<cluster>/cluster-config` to match the current standard
- splits any Kops instance group with more than on subnet into multiple instance groups with a single subnet.
  * it attempts to guess on the correct min/max size of the instance groups by `current min/max / number of subnets` as an integer.
  * it leaves the existing instance group in place to ease the migration
  * there are instructions in each `inventory/<inventory>/clusters/<cluster>/cluster-config/nodes.yml`
- adds audit logging to all kops clusters if not already there
- adds cloud labels to allow cluster-autoscaler auto detect
  * you may still need to add the iam policy to the nodes for it to function properly
- updates the aws-iam-authenticator hook to note require any cloud storage

## Risks:
- the manifold update to the kops clusters will be a multi step process and may incur some risk.

## Follow up tasks:
- the update to the aws-iam-authenticator config no longer requires any cloud storage. Delete the bucket if it exists.
- this version update changes the standards for the EtcD verion. This is a breaking change so it is not handled automatically in this migration.

"""

aws_iam_kops_hook = """
name: kops-hook-authenticator-config.service
before:
  - kubelet.service
roles: [Master]
manifest: |
  [Unit]
    Description=Initialize AWS IAM Authenticator cert and Kube API Server config
  [Service]
    Type=oneshot
    ExecStartPre=/bin/mkdir -p /srv/kubernetes/aws-iam-authenticator
    ExecStartPre=/bin/sh -c '/usr/bin/test -r /srv/kubernetes/aws-iam-authenticator/README || /bin/echo These files were created by the kops-hook-authenticator-config service, which ran aws-iam-authenticator init via a temporary Docker container. >/srv/kubernetes/aws-iam-authenticator/README'
    ExecStartPre=/bin/chown 10000:10000 /srv/kubernetes/aws-iam-authenticator
    ExecStartPost=/bin/sh -c '(/usr/bin/id -u aws-iam-authenticator >/dev/null 2>&1 || /usr/sbin/groupadd -g 10000 aws-iam-authenticator) ; (/usr/bin/id -u aws-iam-authenticator >/dev/null 2>&1 || /usr/sbin/useradd -s /usr/sbin/nologin -c "AWS IAM Authenticator configs" -d /srv/kubernetes/aws-iam-authenticator -u 10000 -g aws-iam-authenticator aws-iam-authenticator)'
    ExecStart=/bin/sh -c '(set -x ; /usr/bin/docker run --net=host --rm -w /srv/kubernetes/aws-iam-authenticator -v /srv/kubernetes/aws-iam-authenticator:/srv/kubernetes/aws-iam-authenticator --name aws-iam-authenticator-initialize gcr.io/heptio-images/authenticator:v0.3.0 init -i clustername ; /bin/mv /srv/kubernetes/aws-iam-authenticator/heptio-authenticator-aws.kubeconfig /srv/kubernetes/aws-iam-authenticator/kubeconfig.yaml)'
"""

audit_log_api_server_settings = {
    'auditLogPath': '/var/log/kube-apiserver-audit.log',
    'auditLogMaxAge': 10,
    'auditLogMaxBackups': 1,
    'auditLogMaxSize': 100,
    'auditPolicyFile': '/srv/kubernetes/audit.yaml'
}

audit_log_file_assets_string = """
name: auditPolicyFile
path: /srv/kubernetes/audit.yaml
roles: [Master]
content: |
  apiVersion: audit.k8s.io/v1beta1
  kind: Policy
  rules:
    # The following requests were manually identified as high-volume and low-risk,
    # so drop them.
    - level: None
      users: ["system:kube-proxy"]
      verbs: ["watch"]
      resources:
        - group: "" # core
          resources: ["endpoints", "services", "services/status"]
    - level: None
      # Ingress controller reads 'configmaps/ingress-uid' through the unsecured port.
      # TODO(#46983): Change this to the ingress controller service account.
      users: ["system:unsecured"]
      namespaces: ["kube-system"]
      verbs: ["get"]
      resources:
        - group: "" # core
          resources: ["configmaps"]
    - level: None
      users: ["kubelet"] # legacy kubelet identity
      verbs: ["get"]
      resources:
        - group: "" # core
          resources: ["nodes", "nodes/status"]
    - level: None
      userGroups: ["system:nodes"]
      verbs: ["get"]
      resources:
        - group: "" # core
          resources: ["nodes", "nodes/status"]
    - level: None
      users:
        - system:kube-controller-manager
        - system:kube-scheduler
        - system:serviceaccount:kube-system:endpoint-controller
      verbs: ["get", "update"]
      namespaces: ["kube-system"]
      resources:
        - group: "" # core
          resources: ["endpoints"]
    - level: None
      users: ["system:apiserver"]
      verbs: ["get"]
      resources:
        - group: "" # core
          resources: ["namespaces", "namespaces/status", "namespaces/finalize"]
    # Don't log HPA fetching metrics.
    - level: None
      users:
        - system:kube-controller-manager
      verbs: ["get", "list"]
      resources:
        - group: "metrics.k8s.io"
    # Don't log these read-only URLs.
    - level: None
      nonResourceURLs:
        - /healthz*
        - /version
        - /swagger*
    # Don't log events requests.
    - level: None
      resources:
        - group: "" # core
          resources: ["events"]
    # node and pod status calls from nodes are high-volume and can be large, don't log responses for expected updates from nodes
    - level: Request
      users: ["kubelet", "system:node-problem-detector", "system:serviceaccount:kube-system:node-problem-detector"]
      verbs: ["update","patch"]
      resources:
        - group: "" # core
          resources: ["nodes/status", "pods/status"]
      omitStages:
        - "RequestReceived"
    - level: Request
      userGroups: ["system:nodes"]
      verbs: ["update","patch"]
      resources:
        - group: "" # core
          resources: ["nodes/status", "pods/status"]
      omitStages:
        - "RequestReceived"
    # deletecollection calls can be large, don't log responses for expected namespace deletions
    - level: Request
      users: ["system:serviceaccount:kube-system:namespace-controller"]
      verbs: ["deletecollection"]
      omitStages:
        - "RequestReceived"
    # Secrets, ConfigMaps, and TokenReviews can contain sensitive & binary data,
    # so only log at the Metadata level.
    - level: Metadata
      resources:
        - group: "" # core
          resources: ["secrets", "configmaps"]
        - group: authentication.k8s.io
          resources: ["tokenreviews"]
      omitStages:
        - "RequestReceived"
    # Get responses can be large; skip them.
    - level: Request
      verbs: ["get", "list", "watch"]
      resources:
        - group: "" # core
        - group: "admissionregistration.k8s.io"
        - group: "apiextensions.k8s.io"
        - group: "apiregistration.k8s.io"
        - group: "apps"
        - group: "authentication.k8s.io"
        - group: "authorization.k8s.io"
        - group: "autoscaling"
        - group: "batch"
        - group: "certificates.k8s.io"
        - group: "extensions"
        - group: "metrics.k8s.io"
        - group: "networking.k8s.io"
        - group: "policy"
        - group: "rbac.authorization.k8s.io"
        - group: "scheduling.k8s.io"
        - group: "settings.k8s.io"
        - group: "storage.k8s.io"
      omitStages:
        - "RequestReceived"
    # Default level for known APIs
    - level: RequestResponse
      resources:
        - group: "" # core
        - group: "admissionregistration.k8s.io"
        - group: "apiextensions.k8s.io"
        - group: "apiregistration.k8s.io"
        - group: "apps"
        - group: "authentication.k8s.io"
        - group: "authorization.k8s.io"
        - group: "autoscaling"
        - group: "batch"
        - group: "certificates.k8s.io"
        - group: "extensions"
        - group: "metrics.k8s.io"
        - group: "networking.k8s.io"
        - group: "policy"
        - group: "rbac.authorization.k8s.io"
        - group: "scheduling.k8s.io"
        - group: "settings.k8s.io"
        - group: "storage.k8s.io"
      omitStages:
        - "RequestReceived"
    # Default level for all other requests.
    - level: Metadata
      omitStages:
        - "RequestReceived"
"""

# Magic to make block formatting in yaml.dump work as expected


class folded_unicode(unicode):
    pass


class literal_unicode(unicode):
    pass


def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)
# https://stackoverflow.com/questions/6432605/any-yaml-libraries-in-python-that-support-dumping-of-long-strings-as-block-liter


class Migration(migration.Migration):
    _starting_version = '2.6.2'
    _ending_version = '2.7.1'

    _readme_string = readme

    def run(self):

        old_nodes_file_name = "nodes.yml"

        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            # If there are no clusters, move on.
            if not os.path.isdir('{}/clusters/'.format(inventory_path)):
                continue

            for cluster_item in os.listdir('{}/clusters/'.format(inventory_path)):
                item_path = '{}/clusters/{}'.format(inventory_path, cluster_item)
                # Is this a kops cluster?

                # There is a small amount of variation here where some cluster config
                # directories are `cluster` and some are `cluster-config`
                # Align these
                if os.path.isdir("{}/cluster".format(item_path)):
                    self.move("{}/cluster".format(item_path), "{}/cluster-config".format(item_path))

                # Remove Post Kops if it exists
                try:
                    os.remove("{}/cluster-config/post-kops.sh".format(item_path, f))
                except Exception:
                    pass

                if os.path.isdir(item_path) and os.path.exists("{}/cluster-config/kops.sh".format(item_path)):
                    logging.info("Migrating {} {}.".format(item, cluster_item))

                    # Start node rejiggering, `if` here for code folding in IDE
                    if True:
                        old_node_groups = "{}/cluster-config/{}".format(item_path, old_nodes_file_name)
                        # Align file names:
                        if not os.path.isfile(old_node_groups):
                            masters = []
                            nodes = []
                            for f in os.listdir("{}/cluster-config/".format(item_path)):
                                if f.endswith('yml') and f != 'cluster.yml':
                                    with open("{}/cluster-config/{}".format(item_path, f)) as yaml_file:
                                        for document in yaml.load_all(yaml_file.read()):
                                            if document.get('kind') == 'InstanceGroup':
                                                if document['spec']['role'] == 'Node':
                                                    for hook in document['spec'].get('hooks', []):
                                                        if hook.get('manifest') is not None:
                                                            hook['manifest'] = literal_unicode(hook['manifest'])
                                                    nodes.append(document)
                                                elif document['spec']['role'] == 'Master':
                                                    for hook in document['spec'].get('hooks', []):
                                                        if hook.get('manifest') is not None:
                                                            hook['manifest'] = literal_unicode(hook['manifest'])
                                                    masters.append(document)
                                                else:
                                                    continue

                                    os.remove("{}/cluster-config/{}".format(item_path, f))
                            with open("{}/cluster-config/{}".format(item_path, 'nodes.yml'), 'w') as nodes_file:
                                nodes_file.write(yaml.dump_all(nodes, default_flow_style=False))

                            with open("{}/cluster-config/{}".format(item_path, 'masters.yml'), 'w') as masters_file:
                                masters_file.write(yaml.dump_all(masters, default_flow_style=False))

                        # Because the nodes.yml may have multiple documents, we need to abuse the YamlEditor class a little bit
                        with open(old_node_groups) as oig:
                            new_node_groups = []
                            for node_group in yaml.load_all(oig.read()):

                                # Keep exisiting node group in the file to ease manual steps
                                for hook in node_group['spec'].get('hooks', []):
                                    if hook.get('manifest') is not None:
                                        hook['manifest'] = literal_unicode(hook['manifest'])

                                new_node_groups.append(node_group)

                                sn_count = len(node_group['spec']['subnets'])
                                cluster_name = node_group['metadata']['labels']['kops.k8s.io/cluster']

                                # Add cloud labels to the existing Node Group
                                # Don't clobber existing cloud labels
                                clabels = node_group['spec'].get('cloudLabels')

                                as_clabels = {
                                    'k8s.io/cluster-autoscaler/enabled': "",
                                    'kubernetes.io/cluster/{}'.format(cluster_name): ""
                                }

                                if clabels:
                                    for key in as_clabels:
                                        if not clabels.get('k8s.io/cluster-autoscaler/enabled'):
                                            clabels[key] = ""
                                else:
                                    node_group['spec']['cloudLabels'] = as_clabels

                                write_message = False
                                if sn_count > 1:
                                    write_message = True
                                    max_size = node_group['spec']['maxSize'] / sn_count
                                    min_size = node_group['spec']['minSize'] / sn_count
                                    name = node_group['metadata']['name']

                                    logging.warn("Creating New Kops Instance Groups for {} group {}. This will require manual intervention."
                                                 .format(cluster_item, node_group['metadata']['name']))
                                    logging.warn("Best guess group sizing: MinSize = {} and MaxSize = {}".format(min_size, max_size))

                                    # Create new instance groups from existing instance group

                                    for subnet in node_group['spec']['subnets']:
                                        new_node_group = deepcopy(node_group)
                                        new_node_group['spec']['subnets'] = [subnet]
                                        new_node_group['spec']['minSize'] = min_size
                                        new_node_group['spec']['maxSize'] = max_size
                                        new_node_group['metadata']['name'] = "{}-{}".format(name, subnet)
                                        new_node_groups.append(new_node_group)

                                with open("{}/cluster-config/{}".format(item_path, 'nodes.yml'), 'w') as nodes_file:
                                    if write_message:
                                        nodes_file.write(ig_message)
                                    nodes_file.write(yaml.dump_all(new_node_groups, default_flow_style=False))
                            # Stop node rejiggering

                    # Setup cluster spec with aws-iam auth and audit logging
                    if True:
                        cluster_spec_file = "{}/cluster-config/cluster.yml".format(item_path)
                        with open(cluster_spec_file) as yaml_file:
                            cluster_config = yaml.load(yaml_file.read())
                            cluster_spec = cluster_config['spec']

                            hooks = cluster_spec.get("hooks")
                            if hooks:
                                logging.debug(hooks)
                                for hook in hooks:
                                    if hook['name'] == 'kops-hook-authenticator-config.service':
                                        kops_hook_index = hooks.index(hook)
                                        logging.debug("Found kops auth hook at index %d", kops_hook_index)
                                    else:
                                        logging.debug("Found other existing hook %s", hook['name'])
                                        hook['manifest'] = literal_unicode(hook['manifest'])

                                logging.debug("Removing existing kops-hook-authenticator-config.service at %d", kops_hook_index)
                                hooks.pop(kops_hook_index)
                            else:
                                logging.debug("No hooks found in cluster spec.")
                                cluster_spec['hooks'] = []

                            for policy_type in cluster_spec.get('additionalPolicies', {}):
                                cluster_spec['additionalPolicies'][policy_type] = literal_unicode(cluster_spec['additionalPolicies'][policy_type])

                            hook = yaml.load(aws_iam_kops_hook)
                            hook['manifest'] = literal_unicode(hook['manifest'])
                            cluster_spec['hooks'].append(hook)

                            file_assets = cluster_spec.get('fileAssets')
                            if not file_assets:
                                cluster_spec['fileAssets'] = []
                                file_assets = cluster_spec['fileAssets']

                            audit_policy_file_assets = yaml.load(audit_log_file_assets_string)

                            existing_audit_file_assets = [ fa for fa in file_assets if fa['name'] == audit_policy_file_assets['name'] ]

                            if len(existing_audit_file_assets) == 0:
                                file_assets.append(audit_policy_file_assets)

                            for fa in file_assets:
                                if fa.get('content'):
                                    fa['content'] = literal_unicode(fa['content'])

                            if not cluster_spec.get('kubeAPIServer'):
                                cluster_spec['kubeAPIServer'] = {}

                            for setting in audit_log_api_server_settings:
                                if cluster_spec['kubeAPIServer'].get(setting) is not None:
                                    cluster_spec['kubeAPIServer'][setting] = audit_log_api_server_settings[setting]

                            if cluster_spec['kubeAPIServer'].get('authenticationTokenWebhookConfigFile') != '/srv/kubernetes/aws-iam-authenticator/kubeconfig.yaml':
                                cluster_spec['kubeAPIServer']['authenticationTokenWebhookConfigFile'] = '/srv/kubernetes/aws-iam-authenticator/kubeconfig.yaml'

                        with open(cluster_spec_file, 'w') as yaml_file:
                            yaml_file.write(yaml.dump(cluster_config, default_flow_style=False))
