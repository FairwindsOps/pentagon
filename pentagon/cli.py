#!/usr/bin/env python
import sys
import os
import click
import logging
import coloredlogs
import traceback
import oyaml as yaml
import json
import pentagon

from pydoc import locate
from pentagon import PentagonException
import migration

from meta import __version__, __author__


class RequiredIf(click.Option):

    def __init__(self, *args, **kwargs):
        self.required_if = kwargs.pop('required_if').split('=')
        self.required_option = self.required_if[0]
        self.required_value = self.required_if[1]
        assert self.required_if, "'required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument required when --%s=%s' %
            (self.required_option, self.required_value)
        ).strip()
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        other_present = self.required_option in opts
        if not other_present or opts[self.required_option] != self.required_value:
            self.prompt = None

        return super(RequiredIf, self).handle_parse_result(
            ctx, opts, args)


@click.group()
@click.version_option(__version__)
@click.option('--log-level', default="INFO", help="Log Level DEBUG,INFO,WARN,ERROR")
@click.pass_context
def cli(ctx, log_level, *args, **kwargs):
    coloredlogs.install(level=log_level)


@click.command()
@click.pass_context
@click.argument('name')
# General directory and file name options
@click.option('-f', '--config-file', help='File to read configuration options from. File supercedes command line options.')
@click.option('-o', '--output-file', default='config.yml', help='File to write options to after completion')
@click.option('--workspace-directory', help='Directory to place new project, defaults to ./')
@click.option('--configure/--no-configure', default=True, help='Configure project with default settings')
@click.option('--force/--no-force', help="Ignore existing directories and copy project")
@click.option('--cloud', default="aws", help="Cloud providor to create default inventory. Defaults to 'aws'. [aws,gcp,none]")
@click.option('--hash-type', default="aws", type=click.Choice(['aws', 'gcp']), help="Type cloud project to create. Defaults to 'aws'")

# General Cloud Options
@click.option('--zones', help="Availability zones as a comma delimited list", cls=RequiredIf, required_if='cloud=gcp')

# Currently only AWS but maybe we can/should add GCP later
@click.option('--configure-vpn/--no-configure-vpn', default=True, help="Whether or not to configure the vpn.")
@click.option('--vpc-name', help="Name of VPC to create")
@click.option('--vpc-cidr-base', help="First two octets of the VPC ip space")
@click.option('--vpc-id', help="AWS VPC id to create the kubernetes clusters in")
@click.option('--admin-vpn-key', help="Name of the ssh key for the admin user of the VPN instance")
@click.option('--vpn-ami-id', help="ami-id to use for the VPN instance")

# General Kubernetes options
@click.option('--kubernetes-version', help="Version of kubernetes to use for cluster nodes")
@click.option('--disk-size', help="Size disk to provision on the kubernetes vms")

# Working
@click.option('--working-kubernetes-cluster-name', help="Name of the working kubernetes cluster nodes")
@click.option('--working-kubernetes-node-count', help="Name of the working kubernetes cluster nodes")
@click.option('--working-kubernetes-node-type', help="Node type of the kube workers")
@click.option('--working-kubernetes-network-cidr', help="Network cidr of the kubernetes working cluster")

# Production
@click.option('--production-kubernetes-cluster-name', help="Name of the production kubernetes cluster nodes")
@click.option('--production-kubernetes-node-count', help="Name of the production kubernetes cluster nodes")
@click.option('--production-kubernetes-node-type', help="Node type of the kube workers")
@click.option('--production-kubernetes-network-cidr', help="Network cidr of the kubernetes working cluster")

# AWS Cloud options
@click.option('--aws-access-key', prompt=True, default=lambda: os.environ.get('PENTAGON_aws_access_key'), help="AWS access key", cls=RequiredIf, required_if='cloud=aws')
@click.option('--aws-secret-key', prompt=True, default=lambda: os.environ.get('PENTAGON_aws_secret_key'), help="AWS secret key", cls=RequiredIf, required_if='cloud=aws')
@click.option('--aws-default-region', help="AWS default region", cls=RequiredIf, required_if='cloud=aws')
@click.option('--aws-availability-zones', help="[Deprecated] Use \"--availability-zones\". AWS availability zones as a comma delimited with spaces. Default to region a, region b, ... region z")
@click.option('--aws-availability-zone-count', help="Number of availability zones to use")
@click.option('--infrastructure-bucket', help="Name of S3 Bucket to store state")
@click.option('--dns-zone', help="DNS zone to configure DNS records in")
@click.option('--create-keys/--no-create-keys', default=True, help="Create ssh keys or not")

# AWS only Kubernetes options
# Working
@click.option('--working-kubernetes-master-aws-zone', help="Availability zone to place the kube master in")
@click.option('--working-kubernetes-master-type', help="AWS only. Node type of the kube master")
@click.option('--working-kube-key', help="Name of the ssh key for the working kubernetes cluster")
@click.option('--working-private-key', help="Name of the ssh key for the working non kubernetes instances")
@click.option('--working-kubernetes-dns-zone', help="DNS Zone of the kubernetes working cluster")
@click.option('--working-kubernetes-v-log-level', help="V Log Level kubernetes working cluster")

# Poduction
@click.option('--production-kubernetes-master-aws-zone', help="Availability zone to place the kube master in")
@click.option('--production-kubernetes-master-type', help=" AWS only. Node type of the kube master")
@click.option('--production-kube-key', help="Name of the ssh key for the production kubernetes cluster")
@click.option('--production-private-key', help="Name of the ssh key for the production non kubernetes instances")
@click.option('--production-kubernetes-dns-zone', help="DNS Zone of the kubernetes production cluster")
@click.option('--production-kubernetes-v-log-level', help="V Log Level kubernetes production cluster")

# GCP Cloud options
@click.option('--gcp-project', prompt=True, help="Google Cloud Project to create clusters in", cls=RequiredIf, required_if='cloud=gcp')
@click.option('--gcp-zones', prompt=True, help="Google Cloud Project zones to create clusters in. Comma separated list.", cls=RequiredIf, required_if='cloud=gcp')
@click.option('--gcp-region', prompt=True, help="Google Cloud Region to create regional resources in", cls=RequiredIf, required_if='cloud=gcp')
def start_project(ctx, name, **kwargs):
    """ Create an infrastructure project from scratch with the configured options """
    try:

        logging.basicConfig(level=kwargs.get('log_level'))
        file_data = {}
        if kwargs.get('config-file'):
            file_data = parse_infile(kwargs.get('config_file'))
        kwargs.update(file_data)
        logging.debug(kwargs)
        cloud = kwargs.get('cloud')
        if cloud.lower() == 'aws':
            project = pentagon.AWSPentagonProject(name, kwargs)
        elif cloud.lower() == 'gcp':
            project = pentagon.GCPPentagonProject(name, kwargs)
        elif cloud.lower() == 'none':
            project = pentagon.PentagonProject(name, kwargs)
        else:
            raise PentagonException("Value passed for option --cloud not 'aws' or 'gcp'")
        logging.debug('Creating {} project {} with {}'.format(cloud.upper(), name, kwargs))
        project.start()
    except Exception as e:
        logging.error(e)
        logging.debug(traceback.format_exc(e))


@click.command()
@click.pass_context
@click.argument('component_path')
@click.option('--data', '-D', multiple=True, help='Individual Key=Value pairs used by the component. There should be no spaces surrounding the `=`')
@click.option('--file', '-f', help='File to read Key=Value pair from (yaml or json are supported)')
@click.option('--out', '-o', default='./', help="Path to output module result, if any")
@click.argument('additional-args', nargs=-1, default=None)
def add(ctx, component_path, additional_args, **kwargs):
    _run('add', component_path, additional_args, kwargs)


@click.command()
@click.pass_context
@click.argument('component_path')
@click.option('--data', '-D', multiple=True, help='Individual Key=Value pairs used by the component')
@click.option('--file', '-f', help='File to read Key=Value pair from (yaml or json are supported)')
@click.option('--out', '-o', default='./', help="Path to output module result, if any")
@click.argument('additional-args', nargs=-1, default=None)
def get(ctx, component_path, additional_args, **kwargs):
    _run('get', component_path, additional_args, kwargs)


@cli.command()
@click.pass_context
@click.option("--dry-run/--no-dry-run", default=False, help="Test migration before applying")
@click.option('--log-level', default="INFO", help="Log Level DEBUG,INFO,WARN,ERROR")
@click.option('--branch', default="migration", help="Name of branch to create for migration. Default='migration'")
@click.option('--yes/--no', default=False, help="Confirm to run migration")
def migrate(ctx, **kwargs):
    """ Update Infrastructure Repository to the latest configuration """
    logging.basicConfig(level=kwargs.get('log_level'))
    migration.migrate(kwargs['branch'], kwargs['yes'])


def _run(action, component_path, additional_args, options):
    logging.basicConfig(level=options.get('log_level'))
    logging.debug("Importing module Pentagon {}".format(component_path))
    logging.debug("with options: {}".format(options))
    logging.debug("and additional arguments: {}".format(additional_args))

    documents = [{}]
    data = parse_data(options.get('data', {}))
    try:
        file = options.get('file', None)
        if file is not None:
            documents = parse_infile(file)
    except Exception as e:
        logging.error("Error parsing data from file or -D arguments")
        logging.error(e)

    component_class = get_component_class(component_path)
    try:
        for data in documents:
            if callable(component_class):
                getattr(component_class(data, additional_args), action)(options.get('out'))
            else:
                logging.error("Error locating module or class: {}".format(component_path))
    except Exception, e:
        logging.error(e)
        logging.debug(traceback.format_exc(e))


# Making names more terminal friendly
cli.add_command(start_project, "start-project")
cli.add_command(add, "add")
cli.add_command(get, "get")


def get_component_class(component_path):
    """ Construct Class path from component input """

    component_path_list = component_path.split(".")
    possible_component_paths = []
    if len(component_path_list) > 1:
        component_name = ".".join(component_path.split(".")[0:-1])
        component_class_name = component_path.split(".")[-1]
    else:
        component_name = component_path
        component_class_name = component_path

    # Compile list of possible class paths
    possible_component_paths.append('{}.{}'.format(component_name, component_class_name))
    possible_component_paths.append('{}.{}'.format(component_name, component_class_name.title()))
    possible_component_paths.append('pentagon.component.{}.{}'.format(component_name, component_class_name))
    possible_component_paths.append('pentagon.component.{}.{}'.format(component_name, component_class_name.title()))
    possible_component_paths.append('pentagon_{}.{}'.format(component_name, component_class_name))
    possible_component_paths.append('pentagon_{}.{}'.format(component_name, component_class_name.title()))

    # Find Class if it exists
    for class_path in possible_component_paths:
        logging.debug('Seeking {}'.format(class_path))
        component_class = locate(class_path)
        if component_class is not None:
            logging.debug("Found {}".format(component_class))
            return component_class

        logging.debug('{} Not found'.format(class_path))


def parse_infile(file):
    """ Parse data structure from file into dictionary for component use """
    with open(file, 'r') as data_file:
        try:
            data = json.load(data_file)
            logging.debug("Data parsed from file {}: {}".format(file, data))
            return data
        except ValueError as json_error:
            pass

        data_file.seek(0)

        try:
            data = list(yaml.load_all(data_file, Loader=yaml.loader.BaseLoader))
            logging.debug("Data parsed from file {}: {}".format(file, data))
            return data
        except yaml.YAMLError as yaml_error:
            pass

    logging.error("Unable to parse in file. {} {} ".format(json_error, yaml_error))


def parse_data(data, d=None):
    """ Function to parse the incoming -D options into a dict """
    if d is None:
        d = {}

    for kv in data:
        key = kv.split('=')[0]
        try:
            val = kv.split('=', 1)[1]
        except IndexError, e:
            val = True

        d[key] = val

    return d
