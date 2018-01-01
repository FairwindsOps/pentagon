
import logging
import os
import shutil
import distutils.dir_util
import sys
import glob

import inspect

from pentagon.migration import migrations
from pentagon import PentagonException

from pydoc import locate
from distutils.version import StrictVersion

default_version = "1.2.0"


def migrate():
    """ Find applicabale migrations and run then """
    for migration in migrations_to_run(current_version(), available_migrations()):
        migration_name = "migration_{}".format(migration.replace('.', '_'))

        migration_class = locate("pentagon.migration.migrations.{}".format(migration_name))
        migration_class.Migration()


def migrations_to_run(current_version, available_migrations):
    try:
        current_index = available_migrations.index(current_version)
    except ValueError, e:
        return None

    return available_migrations[current_index:]


def available_migrations():
    """ Gets and returns a list of migration modules """
    m = []
    for file in glob.glob("{}/migration_*.py".format(migrations.__path__[0])):
        m.append(os.path.basename(os.path.splitext(file)[0]).replace('migration_', '').replace('_', '.'))
    m.sort(key=StrictVersion)
    return m


def installed_version():
    """ get installed version of pentagon """
    import pip
    installed_packages = pip.get_installed_distributions()
    for package in installed_packages:
        if package.key == 'pentagon':
            return package.version


def infrastructure_repository():
    infrastructure_repo = os.environ.get('INFRASTRUCTURE_REPO')
    if infrastructure_repo is None:
        raise PentagonException('Required environnment variable INFRASTRUCTURE_REPO is not set.')
    return infrastructure_repo


def current_version(version_file='.version'):
    """ get current version of the infrastucture_repo """

    version_file = os.path.normpath('{}/{}'.format(infrastructure_repository(), version_file))
    try:
        with open(version_file) as vf:
            version = vf.readline()
    except IOError:
        logging.warn("{} not found. Using default version {}".format(version_file, default_version))
        version = default_version

    return version


class Migration(object):
    """ Parent class for pentagoin migrations """

    def __init__(self):
        self._infrastructure_repository = infrastructure_repository()
        self._temp_repository = os.path.normpath("{}/../.tmp/".format(self._infrastructure_repository))
        self.__prepend_path = self._temp_repository
        self._run()

    def real_path(self, path):
        return os.path.normpath("{}/{}".format(self.__prepend_path, path))

    def _clone(self):
        shutil.copytree(self._infrastructure_repository, self._temp_repository)

    def _run(self):
        self._clone()
        self.run()

    def move(self, source, destination):
        """ move files and directories with extreme predjudice """
        return os.rename(self.real_path(source), self.real_path(destination))
