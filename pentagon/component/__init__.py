import os
import jinja2
import glob
import shutil
import logging
import traceback
import sys
import re

from pentagon.helpers import render_template
from pentagon.defaults import AWSPentagonDefaults as PentagonDefaults


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
        environ_data = {}
        for item in self._environment:
            if type(item) is dict:
                context_var = item.keys()[0]
                env_var = os.environ.get(item.values()[0])
            else:
                context_var = item.lower()
                env_var = os.environ.get(item.upper())

            environ_data[context_var] = env_var

        self._merge_data(environ_data)

    def _process_defaults(self):
        """ Use _defaults from global pentagon defaults, then class and add them to missing values on the _data dict """

        logging.debug('Processing Defaults')
        self._merge_data(self._defaults)

        try:
            class_name = self.__class__.__name__.lower()
            pentagon_defaults = getattr(PentagonDefaults, class_name)
            logging.debug("Adding Pentagon Defaults Last {}".format(pentagon_defaults))
            self._merge_data(pentagon_defaults)
        except AttributeError, e:
            logging.info("No top level defaults for Pentagon component {} ".format(class_name.lower()))

    def _render_directory_templates(self):
        """ Loop and use render_template helper method on all templates in destination directory  """
        template_location = self._destination_directory_name
        if os.path.isfile(self._destination_directory_name):
            template_location = os.path.dirname(self._destination_directory_name)
            logging.debug("{} is a file. Using the directory {} instead.".format(self._destination_directory_name, template_location))
        logging.debug("Rendering Templates in {}".format(template_location))
        for folder, dirnames, files in os.walk(template_location):
            for template in glob.glob(folder + "/*.jinja"):
                logging.debug("Rendering {}".format(template))
                template_file_name = template.split('/')[-1]
                path = '/'.join(template.split('/')[0:-1])
                target_file_name = re.sub(r'\.jinja$', '', template_file_name)
                target = folder + "/" + target_file_name
                render_template(template_file_name, path, target, self._data, overwrite=self._overwrite)

    def _remove_init_file(self):
        """ delete init file, if it exists from template target directory """

        for root, dirs, files in os.walk(self._destination_directory_name):
            for name in files:
                if "__init__.py" == name:
                    logging.debug('Removing: {}'.format(os.path.join(root, name)))
                    os.remove(os.path.join(root, name))

    def _merge_data(self, new_data, clobber=False):
        """ accepts new_data (dict) and clobbber (boolean). Merges dictionary with existing instance dictionary _data. If clobber is True, overwrites value. Defaults to false """
        for key, value in new_data.items():
            if self._data.get(key) is None or clobber:
                logging.debug("Setting component data {}: {}".format(key, value))
                self._data[key] = value

    def add(self, destination, overwrite=False):
        self._destination = destination
        self._overwrite = overwrite
        try:
            self._add_files()
            self._remove_init_file()
            self._render_directory_templates()
        except Exception as e:
            logging.error("Error occured configuring component")
            logging.error(e)
            logging.debug(traceback.format_exc(e))
            sys.exit(1)

    def _add_files(self, sub_path=None):
        """ Copies files and templates from <component>/files """
        if self._overwrite:
            from distutils.dir_util import copy_tree
        else:
            from shutil import copytree as copy_tree
        if sub_path is not None:
            source = ('{}/{}').format(self._files_directory, sub_path)
        else:
            source = self._files_directory

        logging.debug("Adding file: {} -> {}".format(source, self._destination_directory_name))
        if os.path.isfile(source):
            shutil.copy(source, self._destination_directory_name)
        elif os.path.isdir(source):
            copy_tree(source, self._destination_directory_name)
