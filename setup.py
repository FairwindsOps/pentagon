#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

# read in the variables defined in lib/release as global
# to be used below
execfile('lib/pentagon/release.py')

try:
    from setuptools import setup, find_packages
except ImportError:
    print("setup tools required. Please run: "
          "pip install setuptools).")
    sys.exit(1)

setup(name='pentagon',
      version=__version__,
      description='Radically simple kubernetes',
      author=__author__,
      author_email='reactive@reactiveops.com',
      url='http://reactiveops.com/',
      license='GPLv3',
      install_requires=[
        "click==6.7",
        "GitPython==2.1.3",
        "Jinja2==2.9.5",
        "pycrypto==2.6.1",
        "virtualenvwrapper==4.7.2",
        "PyYAML==3.12"
      ],
      package_dir={'': 'lib'},
      packages=find_packages('lib'),
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

# backports-abc==0.4
# certifi==2016.9.26
# cffi==1.7.0
# enum34==1.1.6
# idna==2.1
# ipaddress==1.0.16
# livereload==2.4.1
# Markdown==2.6.7
# MarkupSafe==0.23
# mkdocs==0.16.0
# paramiko==2.0.1
# pyasn1==0.1.9
# pycparser==2.14
# singledispatch==3.4.0.3
# six==1.10.0
# tornado==4.4.2
