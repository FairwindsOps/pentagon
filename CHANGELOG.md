# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 3.1.3
### Changed
- Update dependencies

## 3.1.2
### Fixed
- Changed `defaults.node_count` from 3 to 1, so that only 3 total nodes (one per `InstanceGroup`) are created

## 3.1.1
### Fixed
- In certain cases a migration would cause duplicate hooks
- In certain cases, migrations were not run because kops.sh had been deleted

## 3.1.0
### Fixed
- issue where prompt=true was not respecting the default values 
- display of option values was munging booleans

### Added
- Migration to enable kops hook that patches runc
- validation of prompted valued for click to ensure non-empty strings

## 3.0.2
### Changed
- `TILLER_NAMESPACE` is now set to `tiller` by default

## 3.0.1
### Fixed
- Non-populating values for kubernetes version in gcp deploys
- Bucket not required values for gcp deploys

## 3.0.0
### Added
- Support for GCP / GKE terraform templates on inventory init

### Changed
- Now all pentagon runs will confirm all the values that are set and what the values are set to (one step closer to better transparency)

## 2.7.3
### Fixed
- missing imports for latest migration

## 2.7.2
### Added
- Instructions on how to setup the development environment.
- revised cli help text
- migrations for kops settings that were missed in the last migration
- made `anonymousAuth: false` default for Kops clusters. This currently conflicts with metricserver version > 3.0.0

## 2.7.1
### Fixed
- migration


## 2.7.0 - 2019-1-3

## Updated
- add aws-iam-authenticator to kops spec by default
- Etcd now at version 3 in Kops spec
- default to multiple az instance groups for Kops
- updated generated docs

## Fixed
- kops availability zone calculation


## 2.6.1 - 2018-10-30

## Fixed
- Remove deprecated VPC Terraform module variables.

## 2.6.0 - 2018-10-29

### Updated
- Bumped default VPC Terraform module to version 3.0.0. Removes AWS provider from module in favor of inferred provider.

## 2.5.0 - 2018-10-26

## Fixed
- add new inventory now creates a more complete inventory instead of an empty one
- component arguments may now have '-' or '_'

## Updated
- Docs

## Added
- 'project_name' arg to some components and to the `config.yml` that gets written on 'start-project'

## 2.4.3 - 2018-10-16

### Fixed
- bug where cli -D were not begin passed properly

## 2.4.2 - 2018-10-15
### Updated
- Default Kops settings to improve security and auditing

### Fixed
- Reading from config fil
- Templating local path for ssh_config
- Installation requirements
- Worker and Master variable name for kubernetes arguements

### Added 

### Removed
- Makefiles

## [2.4.1] - 2018-09-21
### Updated

### Fixed

### Added
- PyPi upload to circleci config

## [2.4.0] - 2018-8-21

### Updated
- replaced PyYaml with oyaml and added capability to have multidocument yaml files for component declarations
- Kops cluster `authorization` default changed to rbac
- Updated the inventory config to refer to `${INVENTORY}` vs assigning the `{{name}}` statically. `pentagon/component/inventory/files/common/config/local/vars.yml.jinja`

### Fixed
- `kubernetes_version` parameter value wasn't applying to the kops cluster config from `values.yml` file

## [2.3.1] - 2018-5-30

### Fixed
- Version dependancies

## [2.3.0] - 2018-5-30

### Added
- Some better behavior with migrations where a patch is made but not changes in structure was made

### Updated
- Allowed more value to be optional in the kops templates
- Updated docs
- Bumped terraform-vpc module source version

### Fixed
- Issue where kops clusters were created with the same network cidr

## [2.2.1] - 2018-4-9

## Removed `auto-approve` from terraform Makefile

## [2.2.0] - 2018-3-30

### Added
- colorful logging
- bug fixes and better support for GCP infrastructure
- `--gcp-revion` as part of the above change

### Updated
- `yaml_source` no longer throws errors when file is empty, just logs a message
- made the component class location method more flexible
- reorganized terraform files and made terraform a first class citizen and part of the `inventory.Inventory` component
- renamed vpc.VPC component to aws_vpc.AWSVpc as part of above change
- reorganize the defaul `secrets.yml` and removed unnecessary lines


## [2.1.0] - 2018-2-27

## Added
- `--version` flag to output version
- added cluster auto scaling iam policies by default
- added `--cloud` flag and supporting flags to create GCP/GKE infrastructure

### Updated
- Version handling in setup.py
- Updated yaml loader for config file reading to force string behavior
- Inventory component will use -D name= as the targe directory instead needing -o. 
- Inventory -D account replaced with -D name


## [2.0.0] - 2018-2-1
### Added
- `yaml_source` script to replace env-vars.sh
- Environment variables are now checked in ComponentBase class
- Defaults to component
- overwrite to template rendering
- added inventory component
- added vpn component

### Removed
- env-vars.sh script
- untracked roles directory for ansible

### Updated 
- makefile to support `yaml_source` change
- added distutil.dir_util to allow overwriting exisint directories
- added exit on failure for ComponentBase class
- added default config out file for Pentaong start-project
- updated config file output to sanitize and not include blank values

## [1.2.0] - 2017-11-8
### Added
- Added kops component

### Changed
- Added VPN name to include project name. Allows multiple VPN instances per VPC
- Set default versions to ansible roles
- Updated default kops cluster templates to use new kops component
- Updated make file to use Terraform outputs and improve robustness of creat and destroy
- Fixed legacy authorization bug in gcp coponent

### Removed
- Removed the older kops cluster creation


## [1.1.0] - 2017-10-4
### Added
- Added Changelog
- Added `add` method to `pentagon` command line
- Added component base class
- Added GCP and VPC components
- Added Example component

### Changed
- Changed VPC directory creation to utilize component class instead of 
- Change Click libary usage to "setup tools" method

### Removed
- Section about "changelog" vs "CHANGELOG".

## [1.0.0]

### Added
- First open source version of Pentagon
