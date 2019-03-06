"""
cluster.py
This class has a lot of magic in ComponentBase from pentagon. It can be
difficult to discern what properties, and class vars are needed to make this
run correctly. Best advice I can give to future time travelers is use a
debugger or trial and error.
"""

from pentagon.component import ComponentBase
import pkg_resources


class Public(ComponentBase):
    """
    Adds all the terraform modules that create a single public cluster with
    one node pool. This includes the network, cluster and node pool.
    """

    _required_parameters = [
        'cluster_id',
        'cluster_name',
        'kubernetes_version',
        'network_name',
        'nodes_cidr',
        'nodes_subnetwork_name',
        'pods_cidr',
        'project',
        'region',
        'services_cidr',
        'tf_module_gcp_vpc_native_version',
        'tf_module_gke_module_version',
        'tf_module_nodepool_module_version',
    ]

    _defaults = {
        'cluster_id': '1',
        'network_name': 'kube',
        'nodes_subnetwork_name': 'kube-nodes',
        'region': 'us-central1',
        'tf_module_gcp_vpc_native_version': 'default-v1.0.0',
        'tf_module_gke_module_version': 'public-vpc-native-v1.0.0',
        'tf_module_nodepool_module_version': 'node-pool-v1.0.0',
    }

    @property
    def _files_directory(self):
        _template_path = 'files/public_cluster'
        if pkg_resources.resource_isdir(__name__, _template_path):
            return pkg_resources.resource_filename(__name__, _template_path)
        else:
            raise StandardError(
                'Could not find template path ({})'.format(_template_path))
