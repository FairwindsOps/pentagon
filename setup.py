#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from pentagon.release import __version__, __author__
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Ansible now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

setup(name='pentagon',
      version=__version__,
      description='Radically simple kubernetes',
      author=__author__,
      author_email='reactive@reactiveops.com',
      url='http://reactiveops.com/',
      license='GPLv3',
      # Ansible will also make use of a system copy of python-six if installed but use a
      # Bundled copy if it's not.
      #   install_requires=['paramiko', 'jinja2', "PyYAML", 'setuptools', 'pycrypto >= 2.6'],
      install_requires=[
        "click==6.7",
        "GitPython==2.1.3",
        "Jinja2==2.9.5",
        "pycrypto=2.6.1",
        "virtualenvwrapper==4.7.2"
      ],
      package_dir={'': 'lib'},
      packages=find_packages('lib'),
      # package_data={
      #   '': ['module_utils/*.ps1', 'modules/core/windows/*.ps1', 'modules/extras/windows/*.ps1', 'galaxy/data/*'],
      # },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities',
      ],
      scripts=[
         'bin/pentagon',
         ],
      data_files=[],
      )
