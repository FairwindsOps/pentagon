#!/bin/bash -ex

# source env-vars.sh
# iterate through an array defined here, set an uuper cased env var for each key, as defined in vars.yml
# requires shyaml from https://github.com/0k/shyaml



path_to_yaml_vars="${INFRASTRUCTURE_REPO}/config/local/vars.yml"

LIST_OF_VARIABLES=( "vpc_name" "aws_region" "ansible_config" )
LIST_OF_SECRETS=( "aws_secret_key" )


set_vars() {
for key in  ${LIST_OF_VARIABLES[@]}; do
  # converting to upper case
  upper_case_key=$(echo $key | awk '{print toupper($0)}')

  raw_value=$(cat $path_to_yaml_vars | shyaml get-value $key)

  # some values in vars.yml use other variables that need to be dereferenced
  dereferenced_value=$(eval echo $raw_value)
  export $upper_case_key=$dereferenced_value
done
}

unset_vars() {
  for key in  ${LIST_OF_VARIABLES[@]}; do
    # upper casing
    var=$(echo $key | awk '{print toupper($0)}')
    # unset the env var
    unset $var
  done
}

if  [[  $1 == 'unset' ]] ; then
  unset_vars
else
  set_vars
fi
