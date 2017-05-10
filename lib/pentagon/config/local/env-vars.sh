#!/bin/bash -e

# Usage: source env-vars.sh [unset]
# set/unset environment variables from a specified set of YAML vars set in LIST_OF_CONFIG_VARIABLES or LIST_OF_SECRET_VARIABLES
# two separate files are supported, config vars and secret vars, sourced from separate files
# requires shyaml from https://github.com/0k/shyaml

PATH_TO_CONFIG_VARS="${INFRASTRUCTURE_REPO}/config/local/vars.yml"
PATH_TO_SECRET_VARS="${INFRASTRUCTURE_REPO}/config/private/secrets.yml"

LIST_OF_CONFIG_VARIABLES=( "aws_access_key" "aws_default_region" "ansible_config" "kubeconfig" "infrastructure_bucket")
LIST_OF_SECRET_VARIABLES=( "aws_secret_key" )

##
# Functions
##

set_vars() {
# config vars
for key in  ${LIST_OF_CONFIG_VARIABLES[@]}; do
  # convert to upper case
  upper_case_key=$(echo $key | awk '{print toupper($0)}')

  raw_value=$(cat $PATH_TO_CONFIG_VARS | shyaml get-value $key)
  # some values in vars.yml use other variables that need to be dereferenced
  dereferenced_value=$(eval echo $raw_value)
  export $upper_case_key=$dereferenced_value
done

# secret vars
for key in  ${LIST_OF_SECRET_VARIABLES[@]}; do
  # converting to upper case
  upper_case_key=$(echo $key | awk '{print toupper($0)}')

  raw_value=$(cat $PATH_TO_SECRET_VARS | shyaml get-value $key)
  # some values in vars.yml use other variables that need to be dereferenced
  dereferenced_value=$(eval echo $raw_value)
  export $upper_case_key=$dereferenced_value
done
}

unset_vars() {
  # config vars
  for key in  ${LIST_OF_CONFIG_VARIABLES[@]}; do
    # convert to upper case
    var=$(echo $key | awk '{print toupper($0)}')
    unset $var
  done
  # secret vars
  for key in  ${LIST_OF_SECRET_VARIABLES[@]}; do
    # upper casing
    var=$(echo $key | awk '{print toupper($0)}')
    unset $var
  done
}

if  [[  $1 == 'unset' ]] ; then
  unset_vars
else
  set_vars
fi
