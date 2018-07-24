import datetime


class AWSPentagonDefaults(object):
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
        'kubernetes_version': '1.9.9',
        'network_mask': 24,
        'third_octet': 16,
        'production_third_octet': 16,
        'working_third_octet': 24,
        'third_octet_increment': 1,
        'authorization': {'rbac': {}},
        'networking': {'flannel': {'backend': 'vxlan'}},
        'node_additional_policies': '[{"Effect": "Allow","Action": ["autoscaling:DescribeAutoScalingGroups", "autoscaling:DescribeAutoScalingInstances", "autoscaling:DescribeTags", "autoscaling:SetDesiredCapacity", "autoscaling:TerminateInstanceInAutoScalingGroup"],"Resource": "*"}]',
        'ssh_key_path': '~/.ssh/id_rsa.pub'
    }

    vpc = {
        'vpc_name': datetime.datetime.today().strftime('%Y%m%d'),
        'vpc_cidr_base': '172.20',
        'aws_availability_zone_count': 3,
    }


class GCPPentagonDefaults(object):

    kubernetes = {
        'cluster_version': "1.8.7-gke.1",
        'enable_basic_auth': False,
        'machine_type': 'n1-standard-2',
        'image_type': 'COS',
        'num_nodes': 1,
        'working_cluster_ipv4_cidr': '172.20.0.0/16',
        'production_cluster_ipv4_cidr': '172.21.0.0/16',
        'network': 'default',
        'subnetwork': 'default',
        'enable_autoscaling': True,
        'min_nodes': 1,
        'max_nodes': 3,
        'enable_autoupgrade': True,
        'scopes': [
                    'https://www.googleapis.com/auth/compute',
                    'https://www.googleapis.com/auth/devstorage.read_only',
                    'https://www.googleapis.com/auth/logging.write',
                    'https://www.googleapis.com/auth/monitoring',
                    'https://www.googleapis.com/auth/servicecontrol',
                    'https://www.googleapis.com/auth/service.management.readonly',
                    'https://www.googleapis.com/auth/trace.append'
                  ]

    }
