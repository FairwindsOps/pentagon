# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `yaml_source` script to replace env-vars.sh
- Environment variables are now checked in ComponentBase class
- Defaults to component
- overwrite to template rendering

### Removed
- env-vars.sh script
- untracked roles directory for ansible

### Updated 
- makefile to support `yaml_source` change

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