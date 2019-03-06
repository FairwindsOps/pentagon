from datetime import datetime


class AWSPentagonDefaults(object):
    ssh = {
        'admin_vpn_key': 'admin-vpn',
        'production_kube_key': 'production-kube',
        'production_private_key': 'production-private',
        'working_kube_key': 'working-kube',
        'working_private_key': 'working-private',
    }

    kubernetes = {
        'authorization': {'rbac': {}},
        'kubernetes_version': '1.10.8',
        'master_node_image': '379101102735/debian-stretch-hvm-x86_64-gp2-2018-10-01-66564',
        'master_node_type': 't2.medium',
        'network_cidr': '172.20.0.0/16',
        'network_mask': 24,
        'networking': {'flannel': {'backend': 'vxlan'}},
        'node_additional_policies': '[{"Effect": "Allow","Action": ["autoscaling:DescribeAutoScalingGroups", "autoscaling:DescribeAutoScalingInstances", "autoscaling:DescribeTags", "autoscaling:SetDesiredCapacity", "autoscaling:TerminateInstanceInAutoScalingGroup"],"Resource": "*"}]',
        'node_count': 3,
        'node_root_volume_size': 200,
        'production_third_octet': 16,
        'ssh_key_path': '~/.ssh/id_rsa.pub',
        'third_octet_increment': 1,
        'third_octet': 16,
        'v_log_level': 10,
        'worker_node_image': '379101102735/debian-stretch-hvm-x86_64-gp2-2018-10-01-66564',
        'worker_node_type': 't2.medium',
        'working_third_octet': 24,
    }

    vpc = {
        'aws_availability_zone_count': 3,
        'vpc_cidr_base': '172.20',
        'vpc_name': datetime.today().strftime('%Y%m%d'),
    }
