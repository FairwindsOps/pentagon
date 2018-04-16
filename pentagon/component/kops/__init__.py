import os
import glob
import shutil
import logging
import traceback
import sys
import re
import subprocess
import yaml

from pentagon.component import ComponentBase
from pentagon.helpers import render_template
from pentagon.defaults import AWSPentagonDefaults as PentagonDefaults


class Cluster(ComponentBase):
    _path = os.path.dirname(__file__)

    def add(self, destination):
        for key in PentagonDefaults.kubernetes:
            if not self._data.get(key):
                self._data[key] = PentagonDefaults.kubernetes[key]

        if not self._data.get('network_cidr_base'):
            self._data['network_cidr_base'] = PentagonDefaults.vpc['vpc_cidr_base']

        for key in ['authorization', 'networking']:
            self._data[key] = yaml.dump(self._data[key])

        return super(Cluster, self).add(destination)

    def get(self, destination):

        self._cluster_name = self._data.get('name', os.environ.get('CLUSTER_NAME'))
        self._bucket = self._data.get('kops_state_store', os.environ.get('KOPS_STATE_STORE'))
        self._destination = destination

        if self._bucket is None:
            logging.error("kops_state_store required.")
            sys.exit(1)

        if self._cluster_name is None:
            logging.error("name is required.")
            sys.exit(1)

        os.mkdir(self._cluster_name)
        os.chdir(self._cluster_name)

        self._get_cluster_yaml()

        for ig in self._cluster_instance_groups:
            self._get_instance_group_yaml(ig)

        self._get_cluster_admin_secret()

    @property
    def _cluster_instance_groups(self):
        # get igs yaml
        logging.debug("Getting instance groups.")
        args = ['kops',
                'get',
                'ig',
                '--name={}'.format(self._cluster_name),
                '--state=s3://{}'.format(self._bucket)]

        return [ig.split("\t")[0] for ig in subprocess.check_output(args).split("\n")][1:-1]

    def _get_instance_group_yaml(self, ig):
        args = ['kops',
                'get',
                'ig',
                ig,
                '--name={}'.format(self._cluster_name),
                '--state=s3://{}'.format(self._bucket),
                '-oyaml']

        ig_yaml = subprocess.check_output(args)

        file_mode = 'w'
        if "master" in ig:
            ig_file_name = "master.yml"
            file_mode = 'a'
        else:
            ig_file_name = "{}.yml".format(ig)

        with open(ig_file_name, file_mode) as ig_file:
            ig_file.write("---\n")
            ig_file.write("{}\n".format(ig_yaml))
            ig_file.close()

    def _get_cluster_admin_secret(self):
        # get secret sorta
        logging.debug("Getting ssh key secret. This will require transformation before a new cluster can be created")
        with open('secret.sh', 'w') as sf:
            args = ['kops',
                    'get',
                    'secret',
                    'admin',
                    '--name={}'.format(self._cluster_name),
                    '--state=s3://{}'.format(self._bucket)]

            subprocess.Popen(args, stdout=sf)

    def _get_cluster_yaml(self):
        # get cluster yaml
        logging.debug("Getting cluster.")
        with open('cluster.yml', 'w') as cf:
            args = ['kops',
                    'get',
                    'cluster',
                    '--name={}'.format(self._cluster_name),
                    '--state=s3://{}'.format(self._bucket),
                    '-oyaml']

            p = subprocess.Popen(args, stdout=cf)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                logging.error("Error getting cluster: {}".format(stderr))
                sys.exit(1)
