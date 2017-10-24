#!/bin/bash
set -x
set -e

source $(dirname ${BASH_SOURCE[0]})/../../../account/vars.sh

kops create -f cluster.yml
kops create -f masters.yml
kops create -f nodes.yml
bash ./secret.sh