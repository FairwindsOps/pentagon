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
import yaml
import boto3

from git import Repo, Git
from shutil import copytree, ignore_patterns

import component.kops as kops
import component.inventory as inventory
import component.core as core
from helpers import render_template, write_yaml_file, create_rsa_key
from defaults import PentagonDefaults
from meta import __version__, __author__


class PentagonException(Exception):
    pass


class PentagonProject(object):
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

    def get_arg(self, arg_name, default=None):
        """ Get argument name from click arguments, if it exists, or return default.
            Builtin .get method is inadequate because click defaults to a value of None
            which fools the .get() method """
        if self._args.get(arg_name) is not None:
            return self._args.get(arg_name)
        elif os.environ.get('PENTAGON_{}'.format(arg_name), None) is not None:
            return os.environ.get('PENTAGON_{}'.format(arg_name), None)

        return default

    def __init__(self, name, args={}):
        self._args = args
        self._name = name
        logging.debug(self._args)
        # Set booleans
        self._force = args.get('force')
        self._configure_project = args.get('configure')
        self._create_keys = args.get('create_keys')

        # Does the git repo already exist
        self._git_repo = args.get('git_repo')

        # Set this before it gets overridden by the config file
        self._outfile = self.get_arg('output_file')

        self._config_file = self.get_arg("config_file")
        if self._config_file is not None:
            self._args = self.__read_config_file()

        # Setting local path info
        self._repository_name = os.path.expanduser(self.get_arg("repository_name", "{}-infrastructure".format(name)))
        self._workspace_directory = os.path.expanduser(self.get_arg('workspace_directory', '.'))
        self._repository_directory = "{}/{}".format(
            self._workspace_directory,
            self._repository_name)

        self._private_path = "inventory/default/config/private"

        self._ssh_keys = {
            'admin_vpn_key': self.get_arg('admin_vpn_key', PentagonDefaults.ssh['admin_vpn_key']),
            'working_kube_key': self.get_arg('working_kube_key', PentagonDefaults.ssh['working_kube_key']),
            'production_kube_key': self.get_arg('production_kube_key', PentagonDefaults.ssh['production_kube_key']),
            'working_private_key': self.get_arg('working_private_key', PentagonDefaults.ssh['working_private_key']),
            'production_private_key': self.get_arg('production_private_key', PentagonDefaults.ssh['production_private_key']),
        }

        if self._configure_project:
            # AWS Specific Stuff
            self._aws_access_key = self.get_arg('aws_access_key', self._aws_access_key_placeholder)
            self._aws_secret_key = self.get_arg('aws_secret_key', self._aws_secret_key_placeholder)
            if self.get_arg('aws_default_region'):
                self._aws_default_region = self.get_arg('aws_default_region')
                self._aws_availability_zone_count = int(self.get_arg('aws_availability_zone_count', PentagonDefaults.vpc['aws_availability_zone_count']))
                self._aws_availability_zones = self.get_arg('aws_availability_zones', self.__default_aws_availability_zones())
            else:
                self._aws_default_region = self._aws_default_region_placeholder
                self._aws_availability_zone_count = self._aws_availability_zone_count_placeholder
                self._aws_availability_zones = self._aws_availability_zones_placeholder

            # VPC information
            self._vpc_name = self.get_arg('vpc_name', PentagonDefaults.vpc['vpc_name'])
            self._vpc_cidr_base = self.get_arg('vpc_cidr_base', PentagonDefaults.vpc['vpc_cidr_base'])
            self._vpc_id = self.get_arg('vpc_id', self._vpc_id)

            # DNS
            self._dns_zone = self.get_arg('dns_zone', '{}.com'.format(self._name))

            # KOPS:
            self._infrastructure_bucket = self.get_arg('infrastructure_bucket', self._repository_name)

            # Kubernetes version
            self._kubernetes_version = self.get_arg('kubernetes_version', PentagonDefaults.kubernetes['version'])

            # Working Kubernetes
            self._working_kubernetes_cluster_name = self.get_arg('working_kubernetes_cluster_name', 'working-1.{}'.format(self._dns_zone))
            self._working_kubernetes_dns_zone = self.get_arg('working_kubernetes_dns_zone', '{}'.format(self._dns_zone))

            self._working_kubernetes_node_count = self.get_arg('working_kubernetes_node_count', PentagonDefaults.kubernetes['node_count'])
            self._working_kubernetes_master_aws_zones = self.get_arg('working_kubernetes_master_aws_zones', self._aws_availability_zones)
            self._working_kubernetes_master_node_type = self.get_arg('working_kubernetes_master_node_type', PentagonDefaults.kubernetes['master_node_type'])
            self._working_kubernetes_worker_node_type = self.get_arg('working_kubernetes_worker_node_type', PentagonDefaults.kubernetes['worker_node_type'])
            self._working_kubernetes_v_log_level = self.get_arg('working_kubernetes_v_log_level', PentagonDefaults.kubernetes['v_log_level'])
            self._working_kubernetes_network_cidr = self.get_arg('working_kubernetes_network_cidr', PentagonDefaults.kubernetes['network_cidr'])

            # Production Kubernetes
            self._production_kubernetes_cluster_name = self.get_arg('production_kubernetes_cluster_name', 'production-1.{}'.format(self._dns_zone))
            self._production_kubernetes_dns_zone = self.get_arg('production_kubernetes_dns_zone', '{}'.format(self._dns_zone))

            self._production_kubernetes_node_count = self.get_arg('production_kubernetes_node_count', PentagonDefaults.kubernetes['node_count'])
            self._production_kubernetes_master_aws_zones = self.get_arg('production_kubernetes_master_aws_zones', self._aws_availability_zones)
            self._production_kubernetes_master_node_type = self.get_arg('production_kubernetes_master_node_type', PentagonDefaults.kubernetes['master_node_type'])
            self._production_kubernetes_worker_node_type = self.get_arg('production_kubernetes_worker_node_type', PentagonDefaults.kubernetes['worker_node_type'])
            self._production_kubernetes_v_log_level = self.get_arg('production_kubernetes_v_log_level', PentagonDefaults.kubernetes['v_log_level'])
            self._production_kubernetes_network_cidr = self.get_arg('production_kubernetes_network_cidr', PentagonDefaults.kubernetes['network_cidr'])

    def __write_config_file(self):
        logging.info("Writing arguments to file for Posterity: {}".format(self._outfile))
        config = {}

        if 'output_file' in config:
            config.pop('output_file')

        for key, value in self._args.items():
            if value and key != "aws_access_key" and key != "aws_secret_key":
                config[key] = value

        logging.debug(config)
        try:
            write_yaml_file(self._repository_directory + "/" + self._outfile, config)
        except Exception as e:
            logging.debug(traceback.format_exc(e))
            logging.error("Failed to write arguments to file")
            logging.error(e)

    def __read_config_file(self):
        logging.info("Reading config file: {}".format(self._config_file))
        try:
            with open(self._config_file, "r") as cf:
                config = yaml.load(cf.read(), Loader=yaml.loader.BaseLoader)
                logging.debug("Config values: {}".format(config))
                return config
        except Exception, e:
            logging.info("Failed to read arguments from file")
            logging.error(e)
            sys.exit(1)

        return {}

    def __default_aws_availability_zones(self):
        azs = []
        logging.info("Creating default AWS AZs")
        for i in range(0, self._aws_availability_zone_count):
            azs += ["{}{}".format(self._aws_default_region, self.availability_zone_designations[i])]

        return (", ").join(azs)

    def __repository_directory_exists(self):
        logging.debug("Verifying repository {}".format(self._repository_directory))
        if os.path.isdir(self._repository_directory):
            return True
        return False

    def __git_init(self):
        """ Initialize git repository in the project infrastructure path """
        if self._git_repo:
            return Git().clone(self._git_repo, self._repository_directory)
        else:
            return Repo.init(self._repository_directory)

    def __prepare_context(self):
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
            'aws_region': self._aws_default_region,
            'infrastructure_bucket': self._infrastructure_bucket,
            'vpc_name': self._vpc_name,
            'infrastructure_bucket': self._infrastructure_bucket,
            'aws_region': self._aws_default_region,
            'KOPS_STATE_STORE_BUCKET': self._infrastructure_bucket,
            'org_name': self._name,
            'vpc_name': self._vpc_name,
            'dns_zone': self._dns_zone,
            'vpn_ami_id': self._vpn_ami_id,
            'production_kube_key': self._ssh_keys['production_kube_key'],
            'working_kube_key': self._ssh_keys['working_kube_key'],
            'production_private_key': self._ssh_keys['production_private_key'],
            'working_private_key': self._ssh_keys['working_private_key'],
            'admin_vpn_key': self._ssh_keys['admin_vpn_key'],
            'account': 'default',
        }

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
            'kops_state_store_bucket': self._infrastructure_bucket
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
        }
        write_yaml_file("{}/inventory/default/clusters/production/vars.yml".format(self._repository_directory), context)

    def __get_vpn_ami_id(self):

        self._vpn_ami_id = self._vpn_ami_id_placeholder

        if self.get_arg('configure_vpn'):
            if self.get_arg('vpn_ami_id'):
                self._vpn_ami_id = self.get_arg('vpn_ami_id')
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

    def start(self):

        if not self.__repository_directory_exists() or self._force:
            if not self._git_repo:
                logging.info("Copying project files...")
                self.__create_repo_core()
                self.__git_init()
                self.__configure_default_project()
                if self._outfile is not None:
                    self.__write_config_file()

            with open('{}/.version'.format(self._repository_directory), 'w') as f:
                f.write(__version__)
        else:
            raise PentagonException('Project path exists. Cowardly refusing to overwrite existing project.')

    def delete(self):
        self.__delete()

    def __configure_default_project(self):
            self.__get_vpn_ami_id()
            self.__prepare_context()

            inventory.Inventory(self._context).add('{}/inventory/default'.format(self._repository_directory))
            # self.__prepare_config_private_secrets()
            # self.__prepare_config_local_vars()
            # self.__prepare_ssh_config_vars()
            # self.__prepare_ansible_cfg_vars()
            # self.__prepare_vpn_cfg_vars()
            # self.__prepare_account_vars_yml()
            # self.__prepare_account_vars_sh()

            self.__add_kops_working_cluster()
            self.__add_kops_production_cluster()

    def __create_repo_core(self):
        logging.debug(self._repository_directory)
        core.Core({}).add('{}'.format(self._repository_directory))
    
