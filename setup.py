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
from pentagon import meta

try:
    from setuptools import setup, find_packages
except ImportError:
    print("setup tools required. Please run: "
          "pip install setuptools).")
    sys.exit(1)


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('pentagon/component')

setup(name='pentagon',
      version=meta.__version__,
      description='Radically simple kubernetes',
      author=meta.__author__,
      author_email='services@reactiveops.com',
      url='http://reactiveops.com/',
      license='Apache2.0',
      include_package_data=True,
      install_requires=[
        "click==6.7",
        "GitPython==2.1.3",
        "Jinja2==2.9.5",
        "pycrypto==2.6.1",
        "oyaml>=0.5",
        "shyaml==0.5.0",
        "ansible==2.5.2",
        "boto3==1.7.16",
        "botocore==1.10.29",
        "boto==2.49.0",
        "google-api-python-client==1.6.2",
        "yamlord==0.4",
        "coloredlogs==9.0",
        "awscli==1.15.29",
        "semver>=2.8.0",
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
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
      #package_data={'': extra_files},
      data_files=[],
      )
