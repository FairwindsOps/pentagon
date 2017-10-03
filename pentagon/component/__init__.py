import os
import jinja2
import glob
import shutil
import logging
import traceback
import sys
import re

from pentagon.helpers import render_template


class ComponentBase():
    """ Base class for Pentagon Components. """
    _required_parameters = []

    def __init__(self, data, additional_args=None, **kwargs):

        self._data = data
        self._additional_args = additional_args

        missing_parameters = []
        for item in self._required_parameters:
            if item not in self._data.keys():
                missing_parameters.append(item)

        if missing_parameters:
            logging.error("Missing required data parameters: {}".format(",".join(missing_parameters)))
            sys.exit(1)

    @property
    def _destination_directory_name(self):
        if self._destination != './':
            return self._destination
        return self._data.get('name', self.__class__.__name__.lower())

    @property
    def _files_directory(self):
        return sys.modules[self.__module__].__path__[0] + "/files"

    def add(self, destination):
        """ Copies files and templates from <component>/files and templates the *.jinja files """

        self._destination = destination
        try:
            shutil.copytree(self._files_directory, self._destination_directory_name)

            init_file = self._destination_directory_name + "/__init__.py"
            if os.path.isfile(init_file):
                os.remove(init_file)

            for template in glob.glob(self._destination_directory_name + "/*.jinja"):
                template_file_name = template.split('/')[-1]
                path = '/'.join(template.split('/')[0:-1])
                target_file_name = re.sub(r'\.jinja$', '', template_file_name)
                target = self._destination_directory_name + "/" + target_file_name
                render_template(template_file_name, path, target, self._data)
        except Exception as e:
            logging.error("Error occured configuring component")
            logging.error(e)
            logging.debug(traceback.format_exc(e))
