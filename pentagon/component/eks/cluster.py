

from pentagon.component import ComponentBase




class Cluster(ComponentBase):
    _defaults = {
        'environment': 'test',
        'cluster_name': 'ro-eks',
        'availability_zones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
        'cluster_version': '1.11',
        'subnets': [],
        'instance_type': 'm4.large',
        'vpc_name': 'k8s',
        'vpc_cidr': '10.0.0.0/16',
        'private_subnets': ['10.0.0.0/22', '10.0.4.0/22', '10.0.8.0/22'],
        'public_subnets': ['10.0.12.0/22', '10.0.16.0/22', '10.0.20.0/22']
    }
    def add(self, destination):
        pass

    def get(self, destination):
        pass
