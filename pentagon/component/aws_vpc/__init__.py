import os

from pentagon.component import ComponentBase
from pentagon.defaults import AWSPentagonDefaults as PentagonDefaults
from pentagon.helpers import allege_aws_availability_zones


class AWSVpc(ComponentBase):

    _required_parameters = ['aws_region']

    def add(self, destination, overwrite):
        for key, value in PentagonDefaults.vpc.iteritems():
            if not self._data.get(key):
                self._data[key] = value

        if self._data.get('aws_availability_zones') is None:
            self._data['aws_availability_zones'] = allege_aws_availability_zones(self._data['aws_region'], self._data['aws_availability_zone_count'])

        return super(AWSVpc, self).add(destination, overwrite=overwrite)
