#!/bin/bash -ex

# source env-vars.sh
# iterate through an array defined here, set an uuper cased env var for each key, as defined in vars.yml
# requires shyaml from https://github.com/0k/shyaml

# path_to_yaml_vars=/Users/justin/Documents/work/reactive/workspace/projects/pentagon-proposal/pentagon-proposal-infrastructure/config/local/vars.yml
path_to_yaml_vars="vars.yml"

LIST_OF_VARIABLES=( "vpc_name" "aws_region" )

# for key in  ${LIST_OF_VARIABLES[@]}; do
#   # upper casing
#   var=$(echo $key | awk '{print toupper($0)}')
#   # set the env var
#   export $var="$(cat $path_to_yaml_vars | shyaml get-value $key)"
# done

for key in  ${LIST_OF_VARIABLES[@]}; do
  # upper casing
  var=$(echo $key | awk '{print toupper($0)}')
  # unset the env var
  unset $var
done
