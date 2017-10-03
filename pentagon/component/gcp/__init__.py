import os
import json
import sys

from pentagon.component import ComponentBase
from googleapiclient.discovery import build


class Cluster(ComponentBase):

    @property
    def _files_directory(self):
        return sys.modules[self.__module__].__path__[0] + "/files/cluster"

    def get(self, destination):
        service = build('container', 'v1')
        cl = service.projects().zones().clusters()
        self._zone = self._data.get('zone')
        self._project = self._data.get('project')
        self._destination = destination
        cluster_name = self._data.get('name')
        if cluster_name:
            cluster = cl.get(projectId=self._project, zone=self._zone, clusterId=cluster_name).execute()
            Cluster(self.parse_cluster(cluster)).add(cluster_name)
            self.add_cluster_nodepools(cluster_name, cluster.get('nodePools'))
        else:
            clusters = cl.list(projectId=self._project, zone=self._zone).execute()

            for cluster in clusters['clusters']:
                Cluster(self.parse_cluster(cluster)).add(cluster['name'])
                self.add_cluster_nodepools(cluster.get('name'), cluster.get('nodePools'), self._data.get('get_default_nodepools'))

    def parse_cluster(self, cluster):
        """ parses cluster object returned from api call and converts it to a data structure for the .add() method """

        # remove master zone from additional-zones
        locations = cluster.get('locations')
        locations.remove(self._zone)

        for np in cluster.get('nodePools'):
            if np.get('name') == 'default-pool':
                default_nodepool = np

        return {
                    'project': self._project,
                    'zone': self._zone,
                    'cluster_name': cluster['name'],
                    'cluster_cidr': cluster['clusterIpv4Cidr'],
                    'cluster_version': cluster['currentMasterVersion'],
                    'additional_zones': locations,
                    'disk_size': cluster['nodeConfig']['diskSizeGb'],
                    'max_nodes_per_pool': cluster.get('maxNodesPerPool', None),
                    'image_type': cluster['nodeConfig']['imageType'],
                    'node_labels': cluster.get('nodeLabels', []),
                    'num_nodes': cluster['currentNodeCount'],
                    'image_type': cluster['nodeConfig']['imageType'],
                    'username': cluster['masterAuth']['username'],
                    'network': cluster['network'],
                    'subnetwork': cluster.get('subnetwork', None),
                    'scopes': cluster['nodeConfig']['oauthScopes'],
                    'enable_autoscaling': default_nodepool.get('autoscaling'),
                    'min_nodes': default_nodepool.get('autoscaling', {}).get('minNodeCount'),
                    'max_nodes': default_nodepool.get('autoscaling', {}).get('maxNodeCount'),
                }

    def add_cluster_nodepools(self, cluster_name, nodepools, get_default_nodepools=False):
        """ parses cluster node pools and adds nodepool objects """
        for nodepool in nodepools:
            if nodepool['name'] != 'default-pool' or get_default_nodepools:
                node_data = {'cluster': cluster_name, 'zone': self._zone, 'name': nodepool['name'], 'project': self._project}
                Nodepool(node_data).get(self._destination + '/' + cluster_name + '/nodepools')


class Nodepool(ComponentBase):

    _required_parameters = ['cluster']

    @property
    def _files_directory(self):
        return sys.modules[self.__module__].__path__[0] + "/files/nodepool"

    def get(self, destination):
        service = build('container', 'v1')
        np = service.projects().zones().clusters().nodePools()

        self._name = self._data.get('name')
        self._zone = self._data.get('zone')
        self._project = self._data.get('project')
        self._cluster = self._data.get('cluster')

        if self._data.get('name'):
            pool = np.get(
                            projectId=self._project,
                            zone=self._zone,
                            clusterId=self._cluster,
                            nodePoolId=self._name
                            ).execute()
            Nodepool(self.parse_nodepool(pool)).add(destination + '/' + self._name)

        else:
            nodepools = np.list(
                            projectId=self._project,
                            zone=self._zone,
                            clusterId=self._cluster
                            ).execute()

            for pool in nodepools['nodePools']:
                    Nodepool(self.parse_nodepool(pool)).add(destination + '/' + self._name)

    def parse_nodepool(self, pool):
        """ parses nodepool object returned from api call and converts it to a data structure for the .add() method """        
        return {
                    'nodepool_name': self._name,
                    'project': self._project,
                    'zone': self._zone,
                    'cluster': self._cluster,
                    'disk_size': pool.get('config', {}).get('diskSizeGb'),
                    'image_type': pool.get('config', {}).get('imageType'),
                    'machine_type': pool.get('config', {}).get('machineType'),
                    'node_labels': pool.get('nodeLabels'),
                    'num_nodes': pool.get('numNodes'),
                    'enable_autoscaling': pool.get('autoscaling', {}).get('enabled'),
                    'min_nodes': pool.get('autoscaling', {}).get('minNodeCount'),
                    'max_nodes': pool.get('autoscaling', {}).get('maxNodeCount'),
                    'scopes': pool.get('autoscaling', {}).get('oauthScopes')
                }


class Project(ComponentBase):
    def add(self):
        logging.error("Project component is not yet implemented")
        sys.exit(1)
