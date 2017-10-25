from pentagon.component import ComponentBase
import os
import glob
import shutil
import logging
import traceback
import sys
import re
import subprocess

from pentagon.helpers import render_template


class Cluster(ComponentBase):
    _path = os.path.dirname(__file__)

    def get(self, destination):

        self._cluster_name = self._data.get('name', os.environ.get('CLUSTER_NAME'))
        self._bucket = self._data.get('kops_state_store', os.environ.get('KOPS_STATE_STORE'))
        self._destination = destination

        if self._bucket is None:
            logging.error("kops_state_store required.")
            sys.exit()

        if self._cluster_name is None:
            logging.error("name is required.")
            sys.exit()

        os.mkdir(self._cluster_name)
        os.chdir(self._cluster_name)

        # get cluster yaml
        logging.debug("Getting cluster.")
        with open('cluster.yml', 'w') as cf:
            args = ['kops',
                    'get',
                    'cluster',
                    '--name={}'.format(self._cluster_name),
                    '--state=s3://{}'.format(self._bucket),
                    '-oyaml']
            print " ".join(args)

            subprocess.Popen(args, stdout=cf)

        # get igs yaml
        logging.debug("Getting instance groups.")
        args = ['kops',
                'get',
                'ig',
                '--name={}'.format(self._cluster_name),
                '--state=s3://{}'.format(self._bucket)]

        igs = [ig.split("\t") for ig in subprocess.check_output(args).split("\n")]
        for ig in igs[1:-1]:
            if "master" in ig[0]:
                ig_file = open("master.yml", "a+")
            else:
                ig_file = open("{}.yml".format(ig[0]), "w")
            args = ['kops',
                    'get',
                    'ig',
                    ig[0],
                    '--name={}'.format(self._cluster_name),
                    '--state=s3://{}'.format(self._bucket),
                    '-oyaml']

            ig_file.write("---\n")
            ig_yaml = subprocess.check_output(args)
            ig_file.write("{}\n".format(ig_yaml))
            ig_file.close()

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
