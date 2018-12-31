from copy import deepcopy


from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict

import re
#import oyaml as yaml
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
# 6. Update the ClusterAutoScaler configuration. You should take this opportinity to
#    make it auto disover if appropriate: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md#auto-discovery-setup
# 7. `kops delete` the old, multi-subnet InstanceGroup and delete it from this file
# 8. Delete this comment and check the whole shebang into Git
# 9. Go engage in the relaxing activity of your choice

"""

# TODO: Write up a read me of the changes.
readme = """
cluster-config
post-kops.sh
Node IG update subnets
aws-iam-auth update
auditlogging update

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

# https://reactiveops.slack.com/archives/C34KQUCDC/p1546024063081300

#### Magic to make block formatting in yaml.dump work as expected
class folded_unicode(unicode): pass
class literal_unicode(unicode): pass

def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)
# https://stackoverflow.com/questions/6432605/any-yaml-libraries-in-python-that-support-dumping-of-long-strings-as-block-liter
####


class Migration(migration.Migration):
    _starting_version = '2.6.2'
    _ending_version = '2.7.0'

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
                                                    nodes.append(document)
                                                elif document['spec']['role'] == 'Master':
                                                    masters.append(document)
                                                else:
                                                    continue

                                    os.remove("{}/cluster-config/{}".format(item_path, f))
                            with open("{}/cluster-config/{}".format(item_path, 'nodes.yml'), 'w') as nodes_file:
                                nodes_file.write(yaml.dump_all(nodes, default_flow_style=False))

                            with open("{}/cluster-config/{}".format(item_path, 'masters.yml'), 'w') as masters_file:
                                masters_file.write(yaml.dump_all(nodes, default_flow_style=False))

                        # becauce the nodes.yml may hav multiple documents, we need to abuse the YamlEditor class a little bit
                        with open(old_node_groups) as oig:
                            new_node_groups = []
                            for node_group in yaml.load_all(oig.read()):

                                # Keep exisiting node group in the file to eash manual steps
                                new_node_groups.append(node_group)

                                sn_count = len(node_group['spec']['subnets'])
                                cluster_name = node_group['metadata']['labels']['kops.k8s.io/cluster']

                                # Add cloud labels to the existing Node Group
                                # Don't clobber existin cloud labels
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

                                    logging.info("Creating New Kops Instance Groups for {} group {}".format(cluster_item, node_group['metadata']['name']))
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
                                for hook in hooks:
                                    if hook['name'] == 'kops-hook-authenticator-config.service':
                                        hooks.pop(hooks.index(hook))

                            ### Using the above magic to keep formatting on the literal strings in the yaml

                            for policy_type in cluster_spec.get('additionalPolicies',{}):
                                cluster_spec['additionalPolicies'][policy_type] = literal_unicode(cluster_spec['additionalPolicies'][policy_type])

                            
                            hook = yaml.load(aws_iam_kops_hook)
                            hook['manifest'] = literal_unicode(hook['manifest'])
                            cluster_spec['hooks'].append(hook)

                            if not cluster_spec.get('kubeAPIServer'):
                                cluster_spec['kubeAPIServer'] = {}

                            for setting in audit_log_api_server_settings:
                                if cluster_spec['kubeAPIServer'].get(setting) is not None:
                                    cluster_spec['kubeAPIServer'][setting] = audit_log_api_server_settings[setting]

                            if cluster_spec['kubeAPIServer'].get('authenticationTokenWebhookConfigFile') != '/srv/kubernetes/aws-iam-authenticator/kubeconfig.yaml':
                                cluster_spec['kubeAPIServer']['authenticationTokenWebhookConfigFile'] = '/srv/kubernetes/aws-iam-authenticator/kubeconfig.yaml'

                        with open(cluster_spec_file, 'w') as yaml_file:
                            yaml_file.write(yaml.dump(cluster_config, default_flow_style=False))
