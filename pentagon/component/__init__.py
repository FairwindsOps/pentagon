import os
import jinja2
import glob
import shutil
import logging
import traceback
import sys
import re

from pentagon.helpers import render_template


class ComponentBase(object):
    """ Base class for Pentagon Components. """
    _required_parameters = []

# List of environment variables to use.
# If set, they should override other data sources.
# Lower Case here will find upper case environment variables.
# If a dictionary is passed, the key is the variable name used in context,
# and the value is the environment variable name.
    _environment = []
    _defaults = {}

    def __init__(self, data, additional_args=None, **kwargs):

        self._data = data
        self._additional_args = additional_args
        self._process_env_vars()
        self._process_defaults()

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

    def _process_env_vars(self):
        logging.debug('Fetching environment variables')
        for item in self._environment:
            if type(item) is dict:
                context_var = item.keys()[0]
                env_var = os.environ.get(item.values()[0])
            else:
                context_var = item.lower()
                env_var = os.environ.get(item.upper())
            logging.debug("Setting component variable {}: {}".format(context_var, env_var))
            self._data[context_var] = env_var

    def _process_defaults(self):
        """ Use _defaults from class and add them to missing values on the _data dict """
        logging.debug('Processing Defaults')
        for key, value in self._defaults.items():
            try:
                self._data[key]
            except KeyError, e:
                logging.debug("Setting component variable with default {}: {}".format(key, value))
                self._data[key] = value

    def _render_directory_templates(self):
        """ Loop and use render_template helper method on all templates in destination directory  """
        for template in glob.glob(self._destination_directory_name + "/*.jinja"):
            template_file_name = template.split('/')[-1]
            path = '/'.join(template.split('/')[0:-1])
            target_file_name = re.sub(r'\.jinja$', '', template_file_name)
            target = self._destination_directory_name + "/" + target_file_name
            render_template(template_file_name, path, target, self._data, overwrite=self._overwrite)

    def _remove_init_file(self):
        """ delete init file, if it exists from template target directory """

        init_file = self._destination_directory_name + "/__init__.py"
        if os.path.isfile(init_file):
            os.remove(init_file)

    def add(self, destination, overwrite=False):
        """ Copies files and templates from <component>/files and templates the *.jinja files """
        self._destination = destination
        self._overwrite = overwrite
        try:
            shutil.copytree(self._files_directory, self._destination_directory_name)

            self._remove_init_file()
            self._render_directory_templates()

        except Exception as e:
            logging.error("Error occured configuring component")
            logging.error(e)
            logging.debug(traceback.format_exc(e))
