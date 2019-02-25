
import logging
import os
import shutil
import sys
import glob
import git
import oyaml as yaml
import semver
import fnmatch

from collections import OrderedDict

from pentagon.migration import migrations
from pentagon.pentagon import PentagonException
from pentagon.meta import __version__ as pentagon_version

from pydoc import locate
from distutils.version import StrictVersion

default_version = "1.2.0"
version_file = '.version'
migration_readme_file = 'migrations.md'


def migrate(branch='migration', yes=False):
    """ Find applicable migrations and run them """
    logging.info("Pentagon Version: {}".format(installed_version()))
    logging.info("Starting Repository Version: {}".format(current_version()))

    migrations = migrations_to_run(current_version(), available_migrations())
    if migrations:
        logging.info("There are Migrations to run: ")
        logging.info(migrations)
        if yes:
            for migration in migrations:
                logging.info('Starting migration: {}'.format(migration))
                migration_name = "migration_{}".format(migration.replace('.', '_'))
                migration_class = locate("pentagon.migration.migrations.{}".format(migration_name))
                migration_class.Migration(branch).start()
            logging.info("Migrations complete. Use git to merge the migration branch.")
            logging.info("Current Repository Version: {}".format(current_version()))
        else:
            logging.info("Use: `pentagon migrate --yes` to run migrations")
    else:
        logging.info("No Migrations to run.")
        compare_value = semver.compare(installed_version(), current_version())
        if compare_value == -1:
            logging.error("Repository Version > Installed Version. Upgrade Pentagon")
            sys.exit(1)
        elif compare_value == 1:
            logging.info("Installed Version > Repository Version.")
            logging.info(" Use `pentagon migrate --yes` to update Repository Version")
            if yes:
                Migration(None).version_only()
        elif compare_value == 0:
            logging.info("You are at the latest version!")


def migrations_to_run(current_version, available_migrations):
    m = [v for v in available_migrations if StrictVersion(v) >= StrictVersion(current_version)]
    logging.debug("Migrations to run: {}".format(m))
    return m


def available_migrations():
    """ Gets and returns a list of migration modules """
    m = []
    for file in glob.glob("{}/migration_*.py".format(migrations.__path__[0])):
        m.append(os.path.basename(os.path.splitext(file)[0]).replace('migration_', '').replace('_', '.'))
        logging.debug("Migration Found: {}".format(file))
    m.sort(key=StrictVersion)
    logging.debug("Available Migrations: {}".format(m))
    return m


def installed_version():
    """ get installed version of pentagon """
    return pentagon_version


def infrastructure_repository():
    infrastructure_repo = os.environ.get('INFRASTRUCTURE_REPO')
    if infrastructure_repo is None:
        raise PentagonException('Required environment variable INFRASTRUCTURE_REPO is not set.')
    return infrastructure_repo


def current_version(version_file=version_file):
    """ get current version of the infrastructure_repo """
    try:
        with open("{}/{}".format(infrastructure_repository(), version_file)) as vf:
            version = vf.readline()
    except IOError:
        logging.warn("{} not found. Using default version {}".format(version_file, default_version))
        version = default_version

    return version


class Migration(object):
    """ Parent class for pentagon migrations """

    class YamlEditor(object):

        def __init__(self, file=None):
            # Fetch yaml file as ordered dict
            self.file = file 
            self.data = {}
            if self.file:
                with open(self.file) as yf:
                    self.data = yaml.load(yf.read())
                logging.debug(self.data)
            else:
                logging.debug("YamlEditor initialized with no file")

        def update(self, new_data, clobber=False):
            """ accepts a dict and appends keys to ordered dict. Updates keys if clobber is True"""
            nd = OrderedDict(new_data)
            self.data.update(nd)

        def remove(self, keys):
            """ accepts a list of keys to remove from yaml """
            for key in keys:
                if key in self.data.keys():
                    del self.data[key]

        def get_data(self):
            """ return ordered dict of yaml """
            return self.data

        def write(self, file=None):
            if file is not None:
                self.file = file
                with open(self.file, 'w') as yf:
                    yf.write(yaml.dump(self.data))

        def get(self, key, default=None):
            return self.data.get(key, default)

        def __getitem__(self, key):
            return self.data[key]

        def __setitem__(self, key, value):
            self.data[key] = value

        def __str__(self):
            str(self.data)

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            pass

    def __init__(self, branch_name):
        logging.debug("This got run")
        self._infrastructure_repository = infrastructure_repository()
        self.branch = branch_name

    def start(self):
        """ run migration """
        self._run()

    def version_only(self):
        """ Only increase version in .version_file """
        self.overwrite_file(version_file, installed_version())

    def real_path(self, path):
        return os.path.normpath("{}/{}".format(self._infrastructure_repository, path))

    def _branch(self):
        repo = git.Repo(self._infrastructure_repository)
        try:
            repo.create_head(self.branch)
        except OSError as e:
            logging.error("OSError %s", e)
            logging.error("Most likely the migration branch still exists.  Please delete it and try again.")
            sys.exit(1)

        repo.git.checkout(self.branch)

    def _run(self):
        os.chdir(self._infrastructure_repository)
        self._branch()
        self.run()
        self._write_new_version(installed_version())
        self._append_migration_readme()

    def _write_new_version(self, version):
        """ write new file with new version following the migration """
        self.overwrite_file(version_file, version)

    def _append_migration_readme(self):
        if hasattr(self, "_readme_string"):
            with open(migration_readme_file, 'a+') as mrf:
                mrf.write(self._readme_string)

    def move(self, source, destination):
        """ move files and directories with extreme prejudice """
        logging.info("Moving {} -> {}".format(self.real_path(source), self.real_path(destination)))

        if os.path.isfile(source):
            _move = shutil.move
        elif os.path.exists(destination):
            from distutils.dir_util import copy_tree as _move
        else:
            from shutil import copytree as _move

        _move(self.real_path(source), self.real_path(destination))
        self.delete(source)

    def overwrite_file(self, path, content, executable=False):
        """ alias create_file """
        self.create_file(path, content, executable)

    def create_file(self, path, content, executable=False):
        """ Create a new file """
        path = "{}/{}".format(self._infrastructure_repository, path)
        with open(path, 'w') as f:
            f.write(content)

        if executable is True:
            mode = os.stat(path).st_mode
            mode |= (mode & 0o444) >> 2    # copy R bits to X
            os.chmod(path, mode)

    def create_dir(self, path):
        """ Recursively create a directory """
        path = "{}/{}".format(self._infrastructure_repository, path)
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

    def get_file_content(self, path):
        """ Retreive file contents in a string """
        with open(self.real_path(path), 'r') as f:
            return f.read()

    @property
    def inventory(self, exclude=[]):
        """ Returns list of inventory item, excluding list 'exclude' """
        return [d for d in os.walk("{}/inventory".format(self._infrastructure_repository)).next()[1] if d not in exclude]

    def delete(self, path):
        """ deletes file or directory """
        logging.info("Deleting {}".format(path))
        if os.path.isfile(self.real_path(path)):
            return os.remove(self.real_path(path))

        if os.path.isdir(self.real_path(path)):
            return shutil.rmtree(self.real_path(path))

        return False

    def find_files(self, path='./', file_pattern=None):
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, file_pattern):
                matches.append(os.path.join(root, filename))

        if len(matches) == 0:
            logging.warn("No {} files found!".format(file_pattern))
        return matches
