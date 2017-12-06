#!/usr/bin/env python
import sys
import click
import logging
import traceback
import pentagon
import yaml
import json

from pydoc import locate

from pentagon import PentagonException


@click.group()
@click.pass_context
def cli(ctx):
    pass


@click.command()
@click.pass_context
@click.argument('name')
@click.option('-f', '--config-file', help='File to read configuration options from. File supercedes command line options.')
@click.option('-o', '--output-file', help='File to write options to after completion')
@click.option('--workspace-directory', help='Directory to place new project, defaults to ./')
@click.option('--repository-name', help='Name of the folder to initialize the infrastructure repository')
@click.option('--configure/--no-configure', default=True, help='Configure project with default settings')
@click.option('--force/--no-force', help="Ignore existing directories and copy project")
@click.option('--aws-access-key', help="AWS access key")
@click.option('--aws-secret-key', help="AWS secret key")
@click.option('--aws-default-region', help="AWS default region")
@click.option('--aws-availability-zones', help="AWS availability zones as a comma delimited with spaces. Default to region a, region b, ... region z")
@click.option('--aws-availability-zone-count', help="Number of availability zones to use")
@click.option('--infrastructure-bucket', help="Name of S3 Bucket to store state")
@click.option('--dns-zone', help="DNS zone to configure DNS records in")
@click.option('--git-repo', help="Existing git repository to clone")
@click.option('--create-keys/--no-create-keys', default=True, help="Create ssh keys or not")
@click.option('--admin-vpn-key', help="Name of the ssh key for the admin user of the VPN instance")
@click.option('--working-kube-key', help="Name of the ssh key for the working kubernetes cluster")
@click.option('--production-kube-key', help="Name of the ssh key for the production kubernetes cluster")
@click.option('--working-private-key', help="Name of the ssh key for the working non kubernetes instances")
@click.option('--production-private-key', help="Name of the ssh key for the production non kubernetes instances")
@click.option('--vpc-name', help="Name of VPC to create")
@click.option('--vpc-cidr-base', help="First two octets of the VPC ip space")
@click.option('--vpc-id', help="AWS VPC id to create the kubernetes clusters in")
@click.option('--kubernetes-version', help="Version of kubernetes to use for cluster nodes")
@click.option('--working-kubernetes-cluster-name', help="Name of the working kubernetes cluster nodes")
@click.option('--working-kubernetes-node-count', help="Name of the working kubernetes cluster nodes")
@click.option('--working-kubernetes-master-aws-zone', help="Availability zone to place the kube master in")
@click.option('--working-kubernetes-master-node-type', help="Node type of the kube master")
@click.option('--working-kubernetes-worker-node-type', help="Node type of the kube workers")
@click.option('--working-kubernetes-dns-zone', help="DNS Zone of the kubernetes working cluster")
@click.option('--working-kubernetes-v-log-level', help="V Log Level kubernetes working cluster")
@click.option('--working-kubernetes-network-cidr', help="Network cidr of the kubernetes working cluster")
@click.option('--production-kubernetes-cluster-name', help="Name of the production kubernetes cluster nodes")
@click.option('--production-kubernetes-node-count', help="Name of the production kubernetes cluster nodes")
@click.option('--production-kubernetes-master-aws-zone', help="Availability zone to place the kube master in")
@click.option('--production-kubernetes-master-node-type', help="Node type of the kube master")
@click.option('--production-kubernetes-worker-node-type', help="Node type of the kube workers")
@click.option('--production-kubernetes-dns-zone', help="DNS Zone of the kubernetes production cluster")
@click.option('--production-kubernetes-v-log-level', help="V Log Level kubernetes production cluster")
@click.option('--production-kubernetes-network-cidr', help="Network cidr of the kubernetes working cluster")
@click.option('--configure-vpn/--no-configure-vpn', default=True, help="Whether or not to configure the vpn.")
@click.option('--vpn-ami-id', help="ami-id to use for the VPN instance")
@click.option('--log-level', default="INFO", help="Log Level DEBUG,INFO,WARN,ERROR")
def start_project(ctx, name, **kwargs):
    try:
        logging.basicConfig(level=kwargs.get('log_level'))
        project = pentagon.PentagonProject(name, kwargs)
        project.start()
    except Exception as e:
        logging.error(e)
        logging.debug(traceback.format_exc(e))


@click.command()
@click.pass_context
@click.argument('component_path')
@click.option('--data', '-D', multiple=True, help='Individual Key=Value pairs used by the component')
@click.option('--file', '-f', help='File to read Key=Value pair from (yaml or json are supported)')
@click.option('--out', '-o', default='./', help="Path to output module result, if any")
@click.option('--log-level', default="INFO", help="Log Level DEBUG,INFO,WARN,ERROR")
@click.argument('additional-args', nargs=-1, default=None)
def add(ctx, component_path, additional_args, **kwargs):
    _run('add', component_path, additional_args, kwargs)


@click.command()
@click.pass_context
@click.argument('component_path')
@click.option('--data', '-D', multiple=True, help='Individual Key=Value pairs used by the component')
@click.option('--file', '-f', help='File to read Key=Value pair from (yaml or json are supported)')
@click.option('--out', '-o', default='./', help="Path to output module result, if any")
@click.option('--log-level', default="INFO", help="Log Level DEBUG,INFO,WARN,ERROR")
@click.argument('additional-args', nargs=-1, default=None)
def get(ctx, component_path, additional_args, **kwargs):
    _run('get', component_path, additional_args, kwargs)


def _run(action, component_path, additional_args, options):
    logging.basicConfig(level=options.get('log_level'))
    logging.debug("Importing module Pentagon {}".format(component_path))
    logging.debug("with options: {}".format(options))
    logging.debug("and additional arguments: {}".format(additional_args))

    data = parse_data(options.get('data', {}))
    try:
        file = options.get('file', None)
        if file is not None:
            file_data = parse_infile(file)

            for key in data:
                file_data[key] = data[key]

            data = file_data

    except Exception as e:
        logging.error("Error parsing data from file or -D arguments")
        logging.error(e)

    component_class = get_component_class(component_path)

    try:
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
    if len(component_path_list) > 1:
        component_name = ".".join(component_path.split(".")[0:-1])
        component_class_name = component_path.split(".")[-1].title()
    else:
        component_name = component_path
        component_class_name = component_path.title()

    logging.debug('Seeking pentagon.component.{}.{}'.format(component_name, component_class_name))

    # Find Class if it exists
    component_class = locate("pentagon.component.{}.{}".format(component_name, component_class_name))
    if component_class is None:
        logging.debug('pentagon.component.{}.{} not found'.format(component_name, component_class_name))
        logging.debug('Seeking pentagon.{}.{}'.format(component_name, component_class_name))
        component_class = locate("pentagon_{}.{}".format(component_name, component_class_name))

    logging.debug("Found {}".format(component_class))

    return component_class


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
            data = yaml.load(data_file)
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
