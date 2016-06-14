#!/bin/bash

# source global vars
source ../../account/vars.sh

# source vars in current directory
source ./vars.sh

pushd ${INFRASTRUCTURE_REPO}/vendor/kubernetes/
./get.sh
