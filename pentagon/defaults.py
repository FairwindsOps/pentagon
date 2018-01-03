import datetime


class PentagonDefaults(object):
    ssh = {
        'admin_vpn_key': 'admin-vpn',
        'working_kube_key': 'working-kube',
        'working_private_key': 'working-private',
        'production_kube_key': 'production-kube',
        'production_private_key': 'production-private',
    }

    kubernetes = {
        'node_count': 3,
        'master_node_type': 't2.medium',
        'worker_node_type': 't2.medium',
        'node_root_volume_size': 200,
        'v_log_level': 10,
        'network_cidr': '172.20.0.0/16',
        'version': '1.8.4',
        'network_mask': 24,
        'third_octet': 16,
        'third_octet_increment': 1,
        'authorization': {'alwaysAllow': {}},
        'networking': {'flannel': {}},
    }

    vpc = {
        'name': datetime.datetime.today().strftime('%Y%m%d'),
        'cidr_base': '172.20',
        'aws_availability_zones_count': 3,
    }
