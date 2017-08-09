# from __future__ import (absolute_import, division, print_function)
# __metaclass__ = type

import shlex
import subprocess
import jinja2
import datetime
import shutil
import string
import logging
import yaml
import os
import re
import boto3
import sys

from git import Repo, Git
from shutil import copytree, ignore_patterns
from Crypto.PublicKey import RSA

from pentagon.release import __version__, __author__


class PentagonException(Exception):
    pass


class PentagonProject():
    # DEFAULTS

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

    # Kubernetes version
    _kubernetes_version = '<kubernetes_version>'

    # Working Kubernetes
    _working_kubernetes_cluster_name = '<working_kubernetes_cluster_name>'
    _working_kubernetes_dns_zone = '<working_kubernetes_dns_zone>'
    _working_kubernetes_node_count = '<working_kubernetes_node_count>'
    _working_kubernetes_master_aws_zone = '<working_kubernetes_master_aws_zone>'
    _working_kubernetes_master_node_type = '<working_kubernetes_master_node_type>'
    _working_kubernetes_worker_node_type = '<working_kubernetes_worker_node_type>'
    _working_kubernetes_v_log_level = '<working_kubernetes_v_log_level>'
    _working_kubernetes_network_cidr = '<working_kubernetes_network_cidr>'

    # Production Kubernetes
    _production_kubernetes_cluster_name = '<production_kubernetes_cluster_name>'
    _production_kubernetes_dns_zone = '<production_kubernetes_dns_zone>'
    _production_kubernetes_node_count = '<production_kubernetes_node_count>'
    _production_kubernetes_master_aws_zone = '<production_kubernetes_master_aws_zone>'
    _production_kubernetes_master_node_type = '<production_kubernetes_master_node_type>'
    _production_kubernetes_worker_node_type = '<production_kubernetes_worker_node_type>'
    _production_kubernetes_v_log_level = '<production_kubernetes_v_log_level>'
    _production_kubernetes_network_cidr = '<production_kubernetes_network_cidr>'

    # VPN
    _ami_owners = ['099720109477']  # Amazon AMI owner
    _vpn_ami_id_placeholder = "<ami_id>"
    _vpn_ami_filters = [{'Name': 'virtualization-type', 'Values': ['hvm']},
                        {'Name': 'architecture', 'Values': ['x86_64']},
                        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-trusty*']}]

    default_ssh_keys = {
        'admin_vpn_key': 'admin-vpn',
        'working_kube_key': 'working-kube',
        'working_private_key': 'working-private',
        'production_kube_key': 'production-kube',
        'production_private_key': 'production-private',
    }

    kubernetes_default_version = '1.5.7'

    working_kubernetes_default_values = {
        'working_kubernetes_node_count': 3,
        'working_kubernetes_master_node_type': 't2.medium',
        'working_kubernetes_worker_node_type': 't2.medium',
        'working_kubernetes_v_log_level': 10,
        'working_kubernetes_network_cidr': '172.20.0.0/16',
    }

    production_kubernetes_default_values = {
        'production_kubernetes_node_count': 3,
        'production_kubernetes_master_node_type': 't2.medium',
        'production_kubernetes_worker_node_type': 't2.medium',
        'production_kubernetes_v_log_level': 10,
        'production_kubernetes_network_cidr': '172.20.0.0/16',
    }

    vpc_default_values = {
        'vpc_name': datetime.datetime.today().strftime('%Y%m%d'),
        'vpc_cidr_base': '172.20',
        'aws_availability_zones': 3,
    }

    availability_zone_designations = list(string.ascii_lowercase)

    _project_source = os.path.dirname(__file__)

    @property
    def repository_name(self):
        pass

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

        self._private_path = "{}/config/private/".format(self._repository_directory)

        if self._configure_project:
            # AWS Specific Stuff
            self._aws_access_key = self.get_arg('aws_access_key', self._aws_access_key_placeholder)
            self._aws_secret_key = self.get_arg('aws_secret_key', self._aws_secret_key_placeholder)
            if self.get_arg('aws_default_region'):
                self._aws_default_region = self.get_arg('aws_default_region')
                self._aws_availability_zone_count = int(self.get_arg('aws_availability_zone_count', self.vpc_default_values.get('aws_availability_zones')))
                self._aws_availability_zones = self.get_arg('aws_availability_zones', self.__default_aws_availability_zones())
            else:
                self._aws_default_region = self._aws_default_region_placeholder
                self._aws_availability_zone_count = self._aws_availability_zone_count_placeholder
                self._aws_availability_zones = self._aws_availability_zones_placeholder

            # VPC information
            self._vpc_name = self.get_arg('vpc_name', self.vpc_default_values.get('vpc_name'))
            self._vpc_cidr_base = self.get_arg('vpc_cidr_base', self.vpc_default_values.get('vpc_cidr_base'))
            # Until there exists a vpcid get method...
            self._vpc_id = self.get_arg('vpc_id', self._vpc_id)

            # KOPS:
            self._infrastructure_bucket = self.get_arg('infrastructure_bucket', self._repository_name)

            # Kubernetes version
            self._kubernetes_version = self.get_arg('kubernetes_version', self.kubernetes_default_version)

            # Working Kubernetes
            self._working_kubernetes_cluster_name = self.get_arg('working_kubernetes_cluster_name', 'working-1.{}.com'.format(self._name))
            self._working_kubernetes_dns_zone = self.get_arg('working_kubernetes_dns_zone', 'working.{}.com'.format(self._name))

            self._working_kubernetes_node_count = self.get_arg('working_kubernetes_node_count', self.working_kubernetes_default_values.get('working_kubernetes_node_count'))
            self._working_kubernetes_master_aws_zone = self.get_arg('working_kubernetes_master_aws_zone', self._aws_availability_zones.split(',')[0])
            self._working_kubernetes_master_node_type = self.get_arg('working_kubernetes_master_node_type', self.working_kubernetes_default_values.get('working_kubernetes_master_node_type'))
            self._working_kubernetes_worker_node_type = self.get_arg('working_kubernetes_worker_node_type', self.working_kubernetes_default_values.get('working_kubernetes_worker_node_type'))
            self._working_kubernetes_v_log_level = self.get_arg('working_kubernetes_v_log_level', self.working_kubernetes_default_values.get('working_kubernetes_v_log_level'))
            self._working_kubernetes_network_cidr = self.get_arg('working_kubernetes_network_cidr', self.working_kubernetes_default_values.get('working_kubernetes_network_cidr'))

            # Production Kubernetes
            self._production_kubernetes_cluster_name = self.get_arg('production_kubernetes_cluster_name', 'production-1.{}.com'.format(self._name))
            self._production_kubernetes_dns_zone = self.get_arg('production_kubernetes_dns_zone', 'production.{}.com'.format(self._name))

            self._production_kubernetes_node_count = self.get_arg('production_kubernetes_node_count', self.production_kubernetes_default_values.get('production_kubernetes_node_count'))
            self._production_kubernetes_master_aws_zone = self.get_arg('production_kubernetes_master_aws_zone', self._aws_availability_zones.split(',')[0])
            self._production_kubernetes_master_node_type = self.get_arg('production_kubernetes_master_node_type', self.production_kubernetes_default_values.get('production_kubernetes_master_node_type'))
            self._production_kubernetes_worker_node_type = self.get_arg('production_kubernetes_worker_node_type', self.production_kubernetes_default_values.get('production_kubernetes_worker_node_type'))
            self._production_kubernetes_v_log_level = self.get_arg('production_kubernetes_v_log_level', self.production_kubernetes_default_values.get('production_kubernetes_v_log_level'))
            self._production_kubernetes_network_cidr = self.get_arg('production_kubernetes_network_cidr', self.production_kubernetes_default_values.get('production_kubernetes_network_cidr'))

        # SSH Keys
        self._ssh_keys = {
                          'admin_vpn': self.get_arg('admin_vpn_key', self.default_ssh_keys.get('admin_vpn_key')),
                          'working_kube': self.get_arg('working_kube_key', self.default_ssh_keys.get('working_kube_key')),
                          'production_kube': self.get_arg('production_kube_key', self.default_ssh_keys.get('production_kube_key')),
                          'working_private': self.get_arg('working_private_key', self.default_ssh_keys.get('working_private_key')),
                          'production_private': self.get_arg('production_private_key', self.default_ssh_keys.get('production_private_key')),
                         }

    def __write_config_file(self):
        logging.info("Writing arguments to file for Posterity: {}".format(self._outfile))
        config = self._args
        if 'output_file' in config:
            config.pop('output_file')

        try:
            with open(self._outfile, "w") as f:
                return yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            logging.error("Failed to write arguments to file")
            logging.error(e)

    def __read_config_file(self):
        logging.info("Reading config file: {}".format(self._config_file))
        try:
            with open(self._config_file, "r") as cf:
                config = yaml.load(cf.read())
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

    def __workspace_directory_exists(self):
        logging.debug("Verifying workspace {}".format(self._workspace_directory))
        if os.path.isdir(self._workspace_directory):
            return True
        return False

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

    def __run_commands(self, commands):
        logging.debug(commands)
        stdout, stderr = subprocess.Popen(commands,
                                          shell=True,
                                          executable='/bin/bash',
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE).communicate()
        logging.info(stdout)
        if stderr != '':
            logging.error(stderr)
        return (stdout, stderr)

    def __render_template(self, template_name, template_path, target, context):
        logging.info("Writing {}".format(target))
        logging.debug("Template Context: {}".format(context))
        if os.path.isfile(target):
            logging.warn("Cowardly refusing to overwrite existing file {}".format(target))
            return False

        with open(target, 'w+') as vars_file:
            try:
                template = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path)).get_template(template_name)
                vars_file.write(template.render(context))
            except Exception:
                logging.error("Error writing {}. {}".format(target, sys.exc_info()[0]))
                return False

        logging.debug("Removing {}/{}".format(template_path, template_name))
        os.remove("{}/{}".format(template_path, template_name))

    def __prepare_config_private_secrets(self):
        template_name = "secrets.yml.jinja"
        template_path = "{}/config/private".format(self._repository_directory)
        target = "{}/config/private/secrets.yml".format(self._repository_directory)
        context = {
            'aws_secret_key': self._aws_secret_key,
            'aws_access_key': self._aws_access_key
                   }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_config_local_vars(self):
        template_name = "vars.yml.jinja"
        template_path = "{}/config/local".format(self._repository_directory)
        target = "{}/config/local/vars.yml".format(self._repository_directory)
        context = {
            'org_name': self._name,
            'vpc_name': self._vpc_name,
            'aws_default_region': self._aws_default_region,
            'aws_availability_zones': self._aws_availability_zones,
            'aws_availability_zone_count': self._aws_availability_zone_count,
            'infrastructure_bucket': self._infrastructure_bucket
            }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_tf_vars(self):
        template_name = "terraform.tfvars.jinja"
        template_path = "{}/default/vpc".format(self._repository_directory)
        target = "{}/default/vpc/terraform.tfvars".format(self._repository_directory)
        context = {
            'vpc_name': self._vpc_name,
            'vpc_cidr_base': self._vpc_cidr_base,
            'aws_availability_zones': self._aws_availability_zones,
            'aws_availability_zone_count': self._aws_availability_zone_count,
            'aws_region': self._aws_default_region
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_tf_vpc_module_root(self):
        template_name = "main.tf.jinja"
        template_path = "{}/default/vpc".format(self._repository_directory)
        target = "{}/default/vpc/main.tf".format(self._repository_directory)
        context = {
            'vpc_name': self._vpc_name,
            'infrastructure_bucket': self._infrastructure_bucket,
            'aws_default_region': self._aws_default_region
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_working_kops_vars_sh(self):
        template_name = "vars.sh.jinja"
        template_path = "{}/default/clusters/working/".format(self._repository_directory)
        target = "{}/default/clusters/working/vars.sh".format(self._repository_directory)
        context = {
            'kubernetes_cluster_name': self._working_kubernetes_cluster_name,
            'aws_availability_zones': re.sub(" ", "", self._aws_availability_zones),
            'vpc_id': self._vpc_id,
            'ssh_key_path': "{}{}.pub".format(self._private_path, self._ssh_keys['working_kube']),
            'kubernetes_version': self._kubernetes_version,
            'kubernetes_node_count': self._working_kubernetes_node_count,
            'kubernetes_master_aws_zone': self._working_kubernetes_master_aws_zone,
            'kubernetes_master_node_type': self._working_kubernetes_master_node_type,
            'kubernetes_worker_node_type': self._working_kubernetes_worker_node_type,
            'kubernetes_dns_zone': self._working_kubernetes_dns_zone,
            'kubernetes_v_log_level': self._working_kubernetes_v_log_level,
            'kubernetes_network_cidr': self._working_kubernetes_network_cidr
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_production_kops_vars_sh(self):
        template_name = "vars.sh.jinja"
        template_path = "{}/default/clusters/production/".format(self._repository_directory)
        target = "{}/default/clusters/production/vars.sh".format(self._repository_directory)
        context = {
            'kubernetes_cluster_name': self._production_kubernetes_cluster_name,
            'aws_availability_zones': re.sub(" ", "", self._aws_availability_zones),
            'vpc_id': self._vpc_id,
            'ssh_key_path': "{}{}.pub".format(self._private_path, self._ssh_keys['production_kube']),
            'kubernetes_version': self._kubernetes_version,
            'kubernetes_node_count': self._production_kubernetes_node_count,
            'kubernetes_master_aws_zone': self._production_kubernetes_master_aws_zone,
            'kubernetes_master_node_type': self._production_kubernetes_master_node_type,
            'kubernetes_worker_node_type': self._production_kubernetes_worker_node_type,
            'kubernetes_dns_zone': self._production_kubernetes_dns_zone,
            'kubernetes_v_log_level': self._production_kubernetes_v_log_level,
            'kubernetes_network_cidr': self._production_kubernetes_network_cidr
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_account_vars_sh(self):
        template_name = "vars.sh.jinja"
        template_path = "{}/default/account/".format(self._repository_directory)
        target = "{}/default/account/vars.sh".format(self._repository_directory)
        context = {
            'KOPS_STATE_STORE_BUCKET': self._infrastructure_bucket
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_account_vars_yml(self):
        template_name = "vars.yml.jinja"
        template_path = "{}/default/account/".format(self._repository_directory)
        target = "{}/default/account/vars.yml".format(self._repository_directory)
        context = {
            'org_name': self._name,
            'vpc_name': self._vpc_name
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_ssh_config_vars(self):
        template_name = "ssh_config-default.jinja"
        template_path = "{}/config/local".format(self._repository_directory)
        target = "{}/config/local/ssh_config-default".format(self._repository_directory)
        context = {
            'production_kube_key': self._ssh_keys['production_kube'],
            'working_kube_key': self._ssh_keys['working_kube'],
            'production_private_key': self._ssh_keys['production_private'],
            'working_private_key': self._ssh_keys['working_private'],
            'admin_vpn_key': self._ssh_keys['admin_vpn'],
        }
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_ansible_cfg_vars(self):
        template_name = "ansible.cfg-default.jinja"
        template_path = "{}/config/local".format(self._repository_directory)
        target = "{}/config/local/ansible.cfg-default".format(self._repository_directory)
        context = {}
        return self.__render_template(template_name, template_path, target, context)

    def __prepare_vpn_cfg_vars(self):
        self.__get_vpn_ami_id()
        template_name = "env.yml.jinja"
        template_path = "{}/default/resources/admin-environment".format(self._repository_directory)
        target = "{}/default/resources/admin-environment/env.yml".format(self._repository_directory)
        context = {
            'admin_vpn_key': self._ssh_keys['admin_vpn'],
            'vpn_ami_id': self._vpn_ami_id
        }
        return self.__render_template(template_name, template_path, target, context)

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

                # Set EC2 environ vars for boto3 to use
                os.environ['AWS_ACCESS_KEY'] = self._aws_access_key
                os.environ['AWS_SECRET_KEY'] = self._aws_secret_key
                os.environ['AWS_DEFAULT_REGION'] = self._aws_default_region
                try:
                    client = boto3.client('ec2')
                    images = client.describe_images(Owners=self._ami_owners, Filters=self._vpn_ami_filters)
                    self._vpn_ami_id = images['Images'][-1]['ImageId']
                except Exception, e:
                    logging.error("Encountered \" {} \" getting ami-id. VPN not configured fully. See docs/vpn.md for more information".format(e))
            else:
                logging.warn("Cannot get ami-id without AWS Key, Secret and Default Region set")

    def __create_key(self, name, path, bits=2048):
        key = RSA.generate(bits)

        private_key = "{}{}".format(path, name)
        public_key = "{}{}.pub".format(path, name)

        with open(private_key, 'w') as content_file:
            os.chmod(private_key, 0600)
            content_file.write(key.exportKey('PEM'))

        pubkey = key.publickey()
        with open(public_key, 'w') as content_file:
            content_file.write(pubkey.exportKey('OpenSSH'))

    def __directory_check(self):
        if not self.__workspace_directory_exists():
            msg = "Workspace directory `{0}` does not exist.".format(self._workspace_directory)
            raise PentagonException(msg)

    def start(self):
        self.__directory_check()

        if not self.__repository_directory_exists() or self._force:
            if not self._git_repo:
                logging.info("Copying project files...")
                self.__copy_project_tree()
                self.__git_init()
                self.__render_templates()
                if self._create_keys:
                    self.__create_keys()
                if self._outfile is not None:
                    self.__write_config_file()
        else:
            raise PentagonException('Project path exists. Cowardly refusing to overwrite existing project.')

    def configure_project(self):
        self.__configure_project()

    def delete(self):
        self.__delete()

    def __render_templates(self):

            self.__prepare_config_private_secrets()
            self.__prepare_config_local_vars()
            self.__prepare_ssh_config_vars()
            self.__prepare_ansible_cfg_vars()
            self.__prepare_working_kops_vars_sh()
            self.__prepare_production_kops_vars_sh()
            self.__prepare_tf_vars()
            self.__prepare_tf_vpc_module_root()
            self.__prepare_vpn_cfg_vars()
            self.__prepare_account_vars_yml()
            self.__prepare_account_vars_sh()

    def __create_keys(self):
            key_path = self._private_path
            for key in self._ssh_keys:
                logging.debug("Creating ssh key {}".format(key))
                key_name = "{}".format(self._ssh_keys[key])
                if not os.path.isfile("{}{}".format(key_path, key_name)):
                    self.__create_key(key_name, key_path)
                else:
                    logging.warn("Key {}{} exist!".format(key_path, key_name))

    def __copy_project_tree(self):
        logging.info(self._project_source)
        logging.info(self._repository_directory)
        copytree(self._project_source, self._repository_directory, symlinks=True, ignore=ignore_patterns('__init__.py', '*.pyc', 'release.py'))

class PentagonComponentException(Exception):
    pass

class PentagonComponent():
    def __init__(self, name, args):
        self._name = name
        self._args = args
        self._project_source = os.path.dirname(__file__)
        pass

    def install(self):
        if self._name:
            # the path to the component
            component_path = self._project_source + "/components/{name}".format(name=self._name)
            install_path = component_path + "/install.sh"
            # assemble the command line. based on the Note at https://docs.python.org/2/library/subprocess.html#popen-constructor
            command_line = install_path + ' --component-path ' + component_path
            for key,value in self._args.items():
                if value is not None:
                    command_line += ' --' + key + ' ' + value
            args = shlex.split(command_line)
            try:
                p = subprocess.Popen(args)
            except Exception as e:
                logging.error("Failed to run the install script.")
                logging.error(e)
