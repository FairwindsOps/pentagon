
import os
import logging
import boto3

from pentagon.component import ComponentBase


class Vpn(ComponentBase):

    _required_parameters = [
        'aws_access_key',
        'aws_secret_key',
        'project_name'
    ]

    _ami_owners = ['099720109477']  # Amazon AMI owner
    _vpn_ami_id_placeholder = "<ami_id>"
    _vpn_ami_filters = [{'Name': 'virtualization-type', 'Values': ['hvm']},
                        {'Name': 'architecture', 'Values': ['x86_64']},
                        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-trusty*']}]

    def add(self, destination, overwrite=False):
        self._get_vpn_ami_id()
        return super(Vpn, self).add(destination, overwrite=overwrite)

    def _get_vpn_ami_id(self):

        if self._data.get('vpn_ami_id'):
            self._data['vpn_ami_id'] = self._data.get('vpn_ami_id')
        else:
            logging.info("Getting VPN ami-id from AWS")

            try:
                client = boto3.client('ec2',
                                      aws_access_key_id=self._data['aws_access_key'],
                                      aws_secret_access_key=self._data['aws_secret_key'],
                                      region_name=self._data['aws_default_region']
                                      )
                images = client.describe_images(Owners=self._ami_owners, Filters=self._vpn_ami_filters)
                self._data['vpn_ami_id'] = images['Images'][-1]['ImageId']
            except Exception, e:
                logging.error("Encountered \" {} \" getting ami-id. VPN not configured fully. See docs/vpn.md for more information".format(e))
