#!/usr/bin/env python
# -- coding: utf-8 --
# Copyright 2017 Reactive Ops Inc.
#
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from setuptools import setup, find_packages

try:
    from setuptools import setup, find_packages
except ImportError:
    print("setup tools required. Please run: "
          "pip install setuptools).")
    sys.exit(1)

__version__ = '1.2.0'
__author__ = 'ReactiveOps, Inc.'

setup(name='pentagon',
      version=__version__,
      description='Radically simple kubernetes',
      author=__author__,
      author_email='reactive@reactiveops.com',
      url='http://reactiveops.com/',
      license='Apache2.0',
      include_package_data=True,
      install_requires=[
        "click==6.7",
        "GitPython==2.1.3",
        "Jinja2==2.9.5",
        "pycrypto==2.6.1",
        "PyYAML==3.12",
        "shyaml==0.5.0",
        "ansible==2.3.0.0",
        "boto3==1.4.4",
        "google-api-python-client==1.6.2"
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache License, Version 2.0',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities',
      ],
      entry_points=''' #for click integration
          [console_scripts]
          pentagon=pentagon.cli:cli
      ''',
      packages=find_packages(exclude=['tests', 'example-component']),
      scripts=[
         'bin/yaml_source',
         ],
      )
