# from __future__ import (absolute_import, division, print_function)
# __metaclass__ = type

import datetime
import shutil
import string
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
from helpers import render_template, write_yaml_file, create_rsa_key, merge_dict
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
        self._repository_name = os.path.expanduser("{}-infrastructure".format(name))
        self._repository_directory = "{}".format(
            self._repository_name)

        self._infrastructure_bucket = self.get_data('infrastructure_bucket', self._repository_name)

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
        logging.info("Writing arguments to file for Posterity: {}".format(self._outfile))
        config = {}

        for key, value in self._data.items():
            if value and key not in self.keys_to_sanitize:
                config[key] = value

        logging.debug(config)
        try:
            write_yaml_file(self._repository_directory + "/" + self._outfile, config)
        except Exception as e:
            logging.debug(traceback.format_exc(e))
            logging.error("Failed to write arguments to file")
            logging.error(e)

    def __repository_directory_exists(self):
        """ Tests if the repository directory already exists """
        logging.debug("Checking for repository {}".format(self._repository_directory))
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
            raise PentagonException('Project path exists. Cowardly refusing to overwrite existing project.')

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

    # VPN
    _ami_owners = ['099720109477']  # Amazon AMI owner
    _vpn_ami_id_placeholder = "<ami_id>"
    _vpn_ami_filters = [{'Name': 'virtualization-type', 'Values': ['hvm']},
                        {'Name': 'architecture', 'Values': ['x86_64']},
                        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-trusty*']}]

    availability_zone_designations = list(string.ascii_lowercase)

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
        self._aws_access_key = self.get_data('aws_access_key', self._aws_access_key_placeholder)
        self._aws_secret_key = self.get_data('aws_secret_key', self._aws_secret_key_placeholder)
        if self.get_data('aws_default_region'):
            self._aws_default_region = self.get_data('aws_default_region')
            self._aws_availability_zone_count = int(self.get_data('aws_availability_zone_count', self.PentagonDefaults.vpc['aws_availability_zone_count']))
            self._aws_availability_zones = self.get_data('aws_availability_zones', self.__default_aws_availability_zones())
        else:
            self._aws_default_region = self._aws_default_region_placeholder
            self._aws_availability_zone_count = self._aws_availability_zone_count_placeholder
            self._aws_availability_zones = self._aws_availability_zones_placeholder

        # VPC information
        self._vpc_name = self.get_data('vpc_name', self.PentagonDefaults.vpc['vpc_name'])
        self._vpc_cidr_base = self.get_data('vpc_cidr_base', self.PentagonDefaults.vpc['vpc_cidr_base'])
        self._vpc_id = self.get_data('vpc_id', self._vpc_id)

        # DNS
        self._dns_zone = self.get_data('dns_zone', '{}.com'.format(self._name))

        # Kubernetes version
        self._kubernetes_version = self.get_data('kubernetes_version', self.PentagonDefaults.kubernetes['kubernetes_version'])

        # Working Kubernetes
        self._working_kubernetes_cluster_name = self.get_data('working_kubernetes_cluster_name', 'working-1.{}'.format(self._dns_zone))
        self._working_kubernetes_dns_zone = self.get_data('working_kubernetes_dns_zone', '{}'.format(self._dns_zone))

        self._working_kubernetes_node_count = self.get_data('working_kubernetes_node_count', self.PentagonDefaults.kubernetes['node_count'])
        self._working_kubernetes_master_aws_zones = self.get_data('working_kubernetes_master_aws_zones', self._aws_availability_zones)
        self._working_kubernetes_master_node_type = self.get_data('working_kubernetes_master_node_type', self.PentagonDefaults.kubernetes['master_node_type'])
        self._working_kubernetes_worker_node_type = self.get_data('working_kubernetes_worker_node_type', self.PentagonDefaults.kubernetes['worker_node_type'])
        self._working_kubernetes_v_log_level = self.get_data('working_kubernetes_v_log_level', self.PentagonDefaults.kubernetes['v_log_level'])
        self._working_kubernetes_network_cidr = self.get_data('working_kubernetes_network_cidr', self.PentagonDefaults.kubernetes['network_cidr'])
        self._working_third_octet = self.get_data('working_third_octet', self.PentagonDefaults.kubernetes['working_third_octet'])

        # Production Kubernetes
        self._production_kubernetes_cluster_name = self.get_data('production_kubernetes_cluster_name', 'production-1.{}'.format(self._dns_zone))
        self._production_kubernetes_dns_zone = self.get_data('production_kubernetes_dns_zone', '{}'.format(self._dns_zone))

        self._production_kubernetes_node_count = self.get_data('production_kubernetes_node_count', self.PentagonDefaults.kubernetes['node_count'])
        self._production_kubernetes_master_aws_zones = self.get_data('production_kubernetes_master_aws_zones', self._aws_availability_zones)
        self._production_kubernetes_master_node_type = self.get_data('production_kubernetes_master_node_type', self.PentagonDefaults.kubernetes['master_node_type'])
        self._production_kubernetes_worker_node_type = self.get_data('production_kubernetes_worker_node_type', self.PentagonDefaults.kubernetes['worker_node_type'])
        self._production_kubernetes_v_log_level = self.get_data('production_kubernetes_v_log_level', self.PentagonDefaults.kubernetes['v_log_level'])
        self._production_kubernetes_network_cidr = self.get_data('production_kubernetes_network_cidr', self.PentagonDefaults.kubernetes['network_cidr'])
        self._production_third_octet = self.get_data('production_third_octet', self.PentagonDefaults.kubernetes['production_third_octet'])

    def __default_aws_availability_zones(self):
        azs = []
        logging.info("Creating default AWS AZs")
        for i in range(0, self._aws_availability_zone_count):
            azs += ["{}{}".format(self._aws_default_region, self.availability_zone_designations[i])]

        return (", ").join(azs)

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
            'KOPS_STATE_STORE_BUCKET': self._infrastructure_bucket,
            'dns_zone': self._dns_zone,
            'vpn_ami_id': self._vpn_ami_id,
            'production_kube_key': self._ssh_keys['production_kube_key'],
            'working_kube_key': self._ssh_keys['working_kube_key'],
            'production_private_key': self._ssh_keys['production_private_key'],
            'working_private_key': self._ssh_keys['working_private_key'],
            'admin_vpn_key': self._ssh_keys['admin_vpn_key'],
            'name': 'default',
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
            'third_octet': self._working_third_octet
        }
        write_yaml_file("{}/inventory/default/clusters/working/vars.yml".format(self._repository_directory), context)

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
            'third_octet': self._production_third_octet
        }
        write_yaml_file("{}/inventory/default/clusters/production/vars.yml".format(self._repository_directory), context)

    def __get_vpn_ami_id(self):

        self._vpn_ami_id = self._vpn_ami_id_placeholder

        if self.get_data('configure_vpn'):
            if self.get_data('vpn_ami_id'):
                self._vpn_ami_id = self.get_data('vpn_ami_id')
            elif \
                    self._aws_access_key != self._aws_access_key_placeholder and \
                    self._aws_secret_key != self._aws_secret_key_placeholder and \
                    self._aws_default_region != self._aws_default_region_placeholder:

                logging.info("Getting VPN ami-id from AWS")

                try:
                    client = boto3.client('ec2',
                                          aws_access_key_id=self._aws_access_key,
                                          aws_secret_access_key=self._aws_secret_key,
                                          region_name=self._aws_default_region
                                          )
                    images = client.describe_images(Owners=self._ami_owners, Filters=self._vpn_ami_filters)
                    self._vpn_ami_id = images['Images'][-1]['ImageId']
                except Exception, e:
                    logging.error("Encountered \" {} \" getting ami-id. VPN not configured fully. See docs/vpn.md for more information".format(e))
            else:
                logging.warn("Cannot get ami-id without AWS Key, Secret and Default Region set")

    def configure_default_project(self):
            self.__get_vpn_ami_id()
            inventory.Inventory(self.context).add('{}/inventory/default'.format(self._repository_directory))
            self.__add_kops_working_cluster()
            self.__add_kops_production_cluster()


class GCPPentagonProject(PentagonProject):
    from defaults import GCPPentagonDefaults as PentagonDefaults

    local_defaults = {
        'working_cluster_name': 'working',
        'production_cluster_name': 'production',
    }

    def __init__(self, name, data={}):
        super(GCPPentagonProject, self).__init__(name, data)
        self.default_context = self.PentagonDefaults.kubernetes
        if type(self.default_context['scopes']) == str:
            self.default_context['scopes'] = self.default_context['scopes'].split(',')
        self._data['zones'] = self.get_data('gcp_zones').split(',')
        self.default_context['project'] = self.get_data('gcp_project')

        context = {
            'name': 'default',
            'create_keys': False,
            'cloud': 'gcp',
            'infrastructure_bucket': self._infrastructure_bucket,
            'gcp_zone': self.get_data('zones')[0],
        }

        self._context = merge_dict(self._data, merge_dict(context, self.default_context))

    def add_working_cluster(self):
        context = self.default_context
        context.update({
            'labels': 'cluster=working',
            'zone': self.get_data('zones')[0],
            'node_locations': self.get_data('zones'),
            'cluster_name': self.local_defaults.get('working_cluster_name'),
            'cluster_ipv4_cidr': self.PentagonDefaults.kubernetes['working_cluster_ipv4_cidr']
            })
        gcp.Cluster(context).add('{}/inventory/default/clusters/working'.format(self._repository_directory))

    def add_production_cluster(self):
        context = self.default_context
        context.update({
            'labels': 'cluster=production',
            'zone': self.get_data('zones')[0],
            'locations': self.get_data('zones'),
            'cluster_name': self.local_defaults.get('production_cluster_name'),
            'cluster_ipv4_cidr': self.PentagonDefaults.kubernetes['production_cluster_ipv4_cidr']
            })
        gcp.Cluster(context).add('{}/inventory/default/clusters/production'.format(self._repository_directory))

    def configure_default_project(self):
        inventory.Inventory(self._context).add('{}/inventory/default'.format(self._repository_directory))
        self.add_working_cluster()
        self.add_production_cluster()
