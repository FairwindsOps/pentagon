from copy import deepcopy


from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict

import re
import oyaml as yaml

ig_message = """
# This file has been updated to contain a new set of InstanceGroups with one per Subnet
# The min/max size should be the original size divided by the number of subnets
# In order to put the new InstanceGroups into service you will need to:
# 1. `kops replace -f` this file
# 2. `kops update --yes` this cluster
# 3. ensure the InstanceGroups come up properly
# 4. cordon and drain the old nodes
# 5. Update the ClusterAutoScaler configuration. You should take this opportinity to
#    make it auto disover if appropriate: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md#auto-discovery-setup
# 6. `kops delete` the old, multi-subnet InstanceGroup and delete it from this file
# 7. Delete this comment and check the whole shebang into Git
# 8. Go get pie and ice-cream

"""

class Migration(migration.Migration):
    _starting_version = '2.6.2'
    _ending_version = '2.7.0'

    def run(self):

        old_nodes_file_name = "nodes.yml"

        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            for cluster_item in os.listdir('{}/clusters/'.format(inventory_path)):
                item_path = '{}/clusters/{}'.format(inventory_path, cluster_item)
                # Is this a kops cluster?
                if os.path.isdir(item_path) and os.path.exists("{}/cluster-config/kops.sh".format(item_path)):
                    logging.info("Migrating {} {}.".format(item, cluster_item))
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

                    # Remove Post Kops if it exists
                    try:
                        os.remove("{}/cluster-config/post-kops.sh".format(item_path, f))
                    except Exception:
                        pass

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
                                max_size=node_group['spec']['maxSize'] / sn_count
                                min_size=node_group['spec']['minSize'] / sn_count
                                name=node_group['metadata']['name']

                                logging.info("Creating New Kops Instance Groups for {} group {}".format(cluster_item, node_group['metadata']['name']))
                                logging.warn("Best guess group sizing: MinSize = {} and MaxSize = {}".format(min_size, max_size))

                                # Create new instance groups from existing instance group

                                for subnet in node_group['spec']['subnets']:
                                    new_node_group=deepcopy(node_group)
                                    new_node_group['spec']['subnets']=[subnet]
                                    new_node_group['spec']['minSize']=min_size
                                    new_node_group['spec']['maxSize']=max_size
                                    new_node_group['metadata']['name']="{}-{}".format(name, subnet)
                                    new_node_groups.append(new_node_group)

                            with open("{}/cluster-config/{}".format(item_path, 'nodes.yml'), 'w') as nodes_file:
                                if write_message:
                                    nodes_file.write(ig_message)
                                nodes_file.write(yaml.dump_all(new_node_groups, default_flow_style=False))
