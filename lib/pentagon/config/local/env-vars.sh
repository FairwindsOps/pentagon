#!/bin/bash -e

# Usage: source env-vars.sh [unset]
# set/unset environment variables from a specified set of YAML vars set in LIST_OF_CONFIG_VARIABLES or LIST_OF_SECRET_VARIABLES
# two separate files are supported, config vars and secret vars, sourced from separate files
# requires shyaml from https://github.com/0k/shyaml

LOCAL_CONFIG_DIR=$(dirname ${BASH_SOURCE[0]})

PATH_TO_CONFIG_VARS="${LOCAL_CONFIG_DIR}/vars.yml"
PATH_TO_SECRET_VARS="${LOCAL_CONFIG_DIR}/../private/secrets.yml"

LIST_OF_CONFIG_VARIABLES=( "AWS_DEFAULT_REGION" "ANSIBLE_CONFIG" "KUBECONFIG" "INFRASTRUCTURE_BUCKET")
LIST_OF_SECRET_VARIABLES=( "TF_VAR_aws_access_key" "AWS_ACCESS_KEY" "AWS_ACCESS_KEY_ID" "TF_VAR_aws_secret_key" "AWS_SECRET_KEY" "AWS_SECRET_ACCESS_KEY" )

# export infrastructre repository when it does not already exist
if [[ -z ${INFRASTRUCTURE_REPO+x} ]]
then
  export INFRASTRUCTURE_REPO=$(readlink -f ${LOCAL_CONFIG_DIR}/../../)
fi

##
# Functions
##

set_vars() {
# config vars
for key in  ${LIST_OF_CONFIG_VARIABLES[@]}; do
  raw_value=$(cat $PATH_TO_CONFIG_VARS | shyaml get-value $key)
  # some values in vars.yml use other variables that need to be dereferenced
  dereferenced_value=$(eval echo $raw_value)
  export $key=$dereferenced_value
done

# secret vars
for key in  ${LIST_OF_SECRET_VARIABLES[@]}; do
  raw_value=$(cat $PATH_TO_SECRET_VARS | shyaml get-value $key)
  # some values in vars.yml use other variables that need to be dereferenced
  dereferenced_value=$(eval echo $raw_value)
  export $key=$dereferenced_value
done
}

unset_vars() {
  # config vars
  for key in  ${LIST_OF_CONFIG_VARIABLES[@]}; do
    unset $key
  done
  # secret vars
  for key in  ${LIST_OF_SECRET_VARIABLES[@]}; do
    unset $key
  done
}

if  [[  $1 == 'unset' ]] ; then
  unset_vars
else
  set_vars
fi
