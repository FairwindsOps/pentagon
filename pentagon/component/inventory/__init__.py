import os
import json
import sys

from pentagon.component import ComponentBase
from pentagon.component.vpc import Vpc


class Inventory(ComponentBase):

    _defaults = {'type': 'aws'}

    @property
    def _files_directory(self):
        return sys.modules[self.__module__].__path__[0] + "/files/common"

    def add(self, destination):
        if destination == './':
            destination = './default'

        super(Inventory, self).add(destination)

        if self._data['type'].lower() == 'aws':
            Aws(self._data).add(destination)

        if self._data['type'].lower() == 'gcp':
            Gcp(self._data).add(destination)


class Aws(ComponentBase):

    def add(self, destination):
        Vpc(self._data).add("{}/vpc".format(destination), overwrite=True)


class Gcp(ComponentBase):

    def add(self, destination):
        pass
