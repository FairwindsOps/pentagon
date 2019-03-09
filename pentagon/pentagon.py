# from __future__ import (absolute_import, division, print_function)
# __metaclass__ = type

import datetime
import shutil
import logging
import os
import re
import sys
import traceback
import oyaml as yaml
import boto3

from git import Repo, Git
from shutil import copytree, ignore_patterns

import component.kops as kops
import component.inventory as inventory
import component.core as core
import component.gcp as gcp
from helpers import render_template, write_yaml_file, create_rsa_key, merge_dict, allege_aws_availability_zones
from meta import __version__, __author__


class PentagonException(Exception):
    pass


class PentagonProject(object):
    from defaults import AWSPentagonDefaults as PentagonDefaults
    keys_to_sanitize = ['aws_access_key', 'aws_secret_key', 'output_file']

    def __init__(self, name, data={}):
        self._data = data
        self._name = name
        logging.debug(self._data)
        self._force = self.get_data('force')
        self._configure_project = self.get_data('configure')

        # Set this before it gets overridden by the config file
        self._outfile = self.get_data('output_file')

        # Setting local path info
        self._repository_name = os.path.expanduser(
            "{}-infrastructure".format(name))
        self._repository_directory = "{}".format(
            self._repository_name)

        self._infrastructure_bucket = self.get_data(
            'infrastructure_bucket', self._repository_name)

        self._private_path = "inventory/default/config/private"

    def get_data(self, name, default=None):
        """ Get argument name from click arguments, if it exists, or return default.
            Builtin .get method is inadequate because click defaults to a value of None
            which fools the .get() method """
        if self._data.get(name) is not None:
            return self._data.get(name)
        return default

    def __git_init(self):
        """ Initialize git repository in the project infrastructure path """
        Repo.init(self._repository_directory)

    def __write_config_file(self):
        """ Write sanitized yaml file of starting arguments """
        logging.info(
            "Writing arguments to file for Posterity: {}".format(self._outfile))
        config = {}

        for key, value in self._data.items():
            if value and key not in self.keys_to_sanitize:
                config[key] = value
        config['project_name'] = self._name

        logging.debug(config)
        try:
            write_yaml_file(self._repository_directory +
                            "/" + self._outfile, config)
        except Exception as e:
            logging.debug(traceback.format_exc(e))
            logging.error("Failed to write arguments to file")
            logging.error(e)

    def __repository_directory_exists(self):
        """ Tests if the repository directory already exists """
        logging.debug("Checking for repository {}".format(
            self._repository_directory))
        if os.path.isdir(self._repository_directory):
            return True
            logging.debug("Already Exists")
        logging.debug("Does not exist")
        return False

    def start(self):
        if not self.__repository_directory_exists() or self._force:
            logging.info("Copying project files...")
            self.__create_repo_core()
            self.__git_init()
            self.__write_config_file()
            with open('{}/.version'.format(self._repository_directory), 'w') as f:
                f.write(__version__)

            if self._configure_project is not False:
                self.configure_default_project()
        else:
            raise PentagonException(
                'Project path exists. Cowardly refusing to overwrite existing project.')

    def __create_repo_core(self):
        logging.debug(self._repository_directory)
        core.Core(self._data).add('{}'.format(self._repository_directory))


class AWSPentagonProject(PentagonProject):
    # Placeholders for when there is not sensible default

    # AWS and VPC
    _aws_access_key_placeholder = '<aws-access-key>'
    _aws_secret_key_placeholder = '<aws-secret-key>'
    _aws_default_region_placeholder = '<aws-default-region>'
    _aws_availability_zone_count_placeholder = '<aws-availability-zone-count>'
    _aws_availability_zones_placeholder = '<aws-availability-zones>'

    # VPC
    _vpc_name = '<vpc_name>'
    _vpc_cidr_base = '<vpc_cidr_base>'
    _vpc_id = '<vpc_id>'

    # Working Kubernetes
    _working_kubernetes_cluster_name = '<working_kubernetes_cluster_name>'
    _working_kubernetes_dns_zone = '<working_kubernetes_dns_zone>'
    _working_kubernetes_master_aws_zone = '<working_kubernetes_master_aws_zone>'

    # Production Kubernetes
    _production_kubernetes_cluster_name = '<production_kubernetes_cluster_name>'
    _production_kubernetes_dns_zone = '<production_kubernetes_dns_zone>'
    _production_kubernetes_node_count = '<production_kubernetes_node_count>'
    _production_kubernetes_master_aws_zone = '<production_kubernetes_master_aws_zone>'

    def __init__(self, name, data={}):
        super(AWSPentagonProject, self).__init__(name, data)
        self._create_keys = self.get_data('create_keys')

        self._ssh_keys = {
            'admin_vpn_key': self.get_data('admin_vpn_key', self.PentagonDefaults.ssh['admin_vpn_key']),
            'working_kube_key': self.get_data('working_kube_key', self.PentagonDefaults.ssh['working_kube_key']),
            'production_kube_key': self.get_data('production_kube_key', self.PentagonDefaults.ssh['production_kube_key']),
            'working_private_key': self.get_data('working_private_key', self.PentagonDefaults.ssh['working_private_key']),
            'production_private_key': self.get_data('production_private_key', self.PentagonDefaults.ssh['production_private_key']),
        }

        # AWS Specific Stuff
        self._aws_access_key = self.get_data(
            'aws_access_key', self._aws_access_key_placeholder)
        self._aws_secret_key = self.get_data(
            'aws_secret_key', self._aws_secret_key_placeholder)
        if self.get_data('aws_default_region'):
            self._aws_default_region = self.get_data('aws_default_region')
            self._aws_availability_zone_count = int(self.get_data(
                'aws_availability_zone_count', self.PentagonDefaults.vpc['aws_availability_zone_count']))
            self._aws_availability_zones = self.get_data('aws_availability_zones') or allege_aws_availability_zones(
                self._aws_default_region, self._aws_availability_zone_count)

        else:
            self._aws_default_region = self._aws_default_region_placeholder
            self._aws_availability_zone_count = self._aws_availability_zone_count_placeholder
            self._aws_availability_zones = self._aws_availability_zones_placeholder

        # VPC information
        self._vpc_name = self.get_data(
            'vpc_name', self.PentagonDefaults.vpc['vpc_name'])
        self._vpc_cidr_base = self.get_data(
            'vpc_cidr_base', self.PentagonDefaults.vpc['vpc_cidr_base'])
        self._vpc_id = self.get_data('vpc_id', self._vpc_id)

        # DNS
        self._dns_zone = self.get_data('dns_zone', '{}.com'.format(self._name))

        # Kubernetes version
        self._kubernetes_version = self.get_data(
            'kubernetes_version', self.PentagonDefaults.kubernetes['kubernetes_version'])

        # Working Kubernetes
        self._working_kubernetes_cluster_name = self.get_data(
            'working_kubernetes_cluster_name', 'working-1.{}'.format(self._dns_zone))
        self._working_kubernetes_dns_zone = self.get_data(
            'working_kubernetes_dns_zone', '{}'.format(self._dns_zone))

        self._working_kubernetes_node_count = self.get_data(
            'working_kubernetes_node_count', self.PentagonDefaults.kubernetes['node_count'])
        self._working_kubernetes_master_aws_zones = self.get_data(
            'working_kubernetes_master_aws_zones', self._aws_availability_zones)
        self._working_kubernetes_master_node_type = self.get_data(
            'working_kubernetes_master_node_type', self.PentagonDefaults.kubernetes['master_node_type'])
        self._working_kubernetes_worker_node_type = self.get_data(
            'working_kubernetes_worker_node_type', self.PentagonDefaults.kubernetes['worker_node_type'])
        self._working_kubernetes_v_log_level = self.get_data(
            'working_kubernetes_v_log_level', self.PentagonDefaults.kubernetes['v_log_level'])
        self._working_kubernetes_network_cidr = self.get_data(
            'working_kubernetes_network_cidr', self.PentagonDefaults.kubernetes['network_cidr'])
        self._working_third_octet = self.get_data(
            'working_third_octet', self.PentagonDefaults.kubernetes['working_third_octet'])

        # Production Kubernetes
        self._production_kubernetes_cluster_name = self.get_data(
            'production_kubernetes_cluster_name', 'production-1.{}'.format(self._dns_zone))
        self._production_kubernetes_dns_zone = self.get_data(
            'production_kubernetes_dns_zone', '{}'.format(self._dns_zone))

        self._production_kubernetes_node_count = self.get_data(
            'production_kubernetes_node_count', self.PentagonDefaults.kubernetes['node_count'])
        self._production_kubernetes_master_aws_zones = self.get_data(
            'production_kubernetes_master_aws_zones', self._aws_availability_zones)
        self._production_kubernetes_master_node_type = self.get_data(
            'production_kubernetes_master_node_type', self.PentagonDefaults.kubernetes['master_node_type'])
        self._production_kubernetes_worker_node_type = self.get_data(
            'production_kubernetes_worker_node_type', self.PentagonDefaults.kubernetes['worker_node_type'])
        self._production_kubernetes_v_log_level = self.get_data(
            'production_kubernetes_v_log_level', self.PentagonDefaults.kubernetes['v_log_level'])
        self._production_kubernetes_network_cidr = self.get_data(
            'production_kubernetes_network_cidr', self.PentagonDefaults.kubernetes['network_cidr'])
        self._production_third_octet = self.get_data(
            'production_third_octet', self.PentagonDefaults.kubernetes['production_third_octet'])

        self._vpn_ami_id = self.get_data('vpn_ami_id')

    @property
    def context(self):
        self._context = {
            'aws_secret_key': self._aws_secret_key,
            'aws_access_key': self._aws_access_key,
            'org_name': self._name,
            'vpc_name': self._vpc_name,
            'aws_default_region': self._aws_default_region,
            'aws_availability_zones': self._aws_availability_zones,
            'aws_availability_zone_count': self._aws_availability_zone_count,
            'infrastructure_bucket': self._infrastructure_bucket,
            'vpc_name': self._vpc_name,
            'vpc_cidr_base': self._vpc_cidr_base,
            'aws_availability_zones': self._aws_availability_zones,
            'aws_availability_zone_count': self._aws_availability_zone_count,
            'infrastructure_bucket': self._infrastructure_bucket,
            'vpc_name': self._vpc_name,
            'infrastructure_bucket': self._infrastructure_bucket,
            'aws_region': self._aws_default_region,
            'dns_zone': self._dns_zone,
            'vpn_ami_id': self._vpn_ami_id,
            'production_kube_key': self._ssh_keys['production_kube_key'],
            'working_kube_key': self._ssh_keys['working_kube_key'],
            'production_private_key': self._ssh_keys['production_private_key'],
            'working_private_key': self._ssh_keys['working_private_key'],
            'admin_vpn_key': self._ssh_keys['admin_vpn_key'],
            'name': 'default',
            'project_name': self._name,
            'configure_vpn': self.get_data('configure_vpn'),
        }
        logging.debug(self._context)
        return self._context

    def __add_kops_working_cluster(self):
        context = {
            'cluster_name': self._working_kubernetes_cluster_name,
            'availability_zones': re.sub(" ", "", self._aws_availability_zones).split(","),
            'vpc_id': self._vpc_id,
            'ssh_key_path': "${{INFRASTRUCTURE_REPO}}/{}/{}.pub".format(self._private_path, self._ssh_keys['working_kube_key']),
            'kubernetes_version': self._kubernetes_version,
            'ig_max_size': self._working_kubernetes_node_count,
            'ig_min_size': self._working_kubernetes_node_count,
            'master_availability_zones': [zone.strip() for zone in self._working_kubernetes_master_aws_zones.split(',')],
            'master_node_type': self._working_kubernetes_master_node_type,
            'worker_node_type': self._working_kubernetes_worker_node_type,
            'cluster_dns': self._working_kubernetes_dns_zone,
            'kubernetes_v_log_level': self._working_kubernetes_v_log_level,
            'network_cidr': self._working_kubernetes_network_cidr,
            'network_cidr_base': self._vpc_cidr_base,
            'kops_state_store_bucket': self._infrastructure_bucket,
            'third_octet': self._working_third_octet,
        }
        write_yaml_file(
            "{}/inventory/default/clusters/working/vars.yml".format(self._repository_directory), context)

    def __add_kops_production_cluster(self):
        context = {
            'cluster_name': self._production_kubernetes_cluster_name,
            'availability_zones': re.sub(" ", "", self._aws_availability_zones).split(","),
            'vpc_id': self._vpc_id,
            'ssh_key_path': "${{INFRASTRUCTURE_REPO}}/{}/{}.pub".format(self._private_path, self._ssh_keys['production_kube_key']),
            'kubernetes_version': self._kubernetes_version,
            'ig_max_size': self._production_kubernetes_node_count,
            'ig_min_size': self._production_kubernetes_node_count,
            'master_availability_zones': [zone.strip() for zone in self._production_kubernetes_master_aws_zones.split(',')],
            'master_node_type': self._production_kubernetes_master_node_type,
            'worker_node_type': self._production_kubernetes_worker_node_type,
            'cluster_dns': self._production_kubernetes_dns_zone,
            'kubernetes_v_log_level': self._production_kubernetes_v_log_level,
            'network_cidr': self._production_kubernetes_network_cidr,
            'network_cidr_base': self._vpc_cidr_base,
            'kops_state_store_bucket': self._infrastructure_bucket,
            'third_octet': self._production_third_octet,
        }
        write_yaml_file(
            "{}/inventory/default/clusters/production/vars.yml".format(self._repository_directory), context)

    def configure_default_project(self):
        inventory.Inventory(self.context).add(
            '{}/inventory/default'.format(self._repository_directory))
        self.__add_kops_working_cluster()
        self.__add_kops_production_cluster()


class GCPPentagonProject(PentagonProject):

    def __init__(self, name, data={}):
        # Build translated data for inventory input
        self._gcp_inventory_context = self._build_inv_params(name, data)
        # Add the project_name since it isn't passed in from click
        self._gcp_inventory_context['project_name'] = name
        self._gcp_inventory_context['project'] = self._gcp_inventory_context['gcp_project']
        self._gcp_inventory_context['name'] = name
        super(GCPPentagonProject, self).__init__(name, data)

    @staticmethod
    def _build_inv_params(name, input_context):
        gcp_context = input_context.copy()
        inventory_map = {
            'gcp_nodes_cidr': 'nodes_cidr',
            'gcp_services_cidr': 'services_cidr',
            'gcp_pods_cidr': 'pods_cidr',
            'gcp_cluster_name': 'cluster_name',
            'gcp_kubernetes_version': 'kubernetes_version',
            'gcp_infra_bucket': 'infrastructure_bucket',
        }

        for old_key, new_key in inventory_map.iteritems():
            if new_key in gcp_context.keys():
                if gcp_context[new_key]:
                    raise KeyError(
                        'Key already exists, this should not happen.')
            gcp_context[new_key] = gcp_context.pop(old_key)

        # for two levels downstream into gke generator tf
        gcp_context['region'] = gcp_context['gcp_region']

        return gcp_context

    def configure_default_project(self):
        inventory.Inventory(self._gcp_inventory_context).add(
            '{}/inventory/{}'.format(
                self._repository_directory,
                self._gcp_inventory_context['project']
            )
        )
