#!/bin/bash
set -x
set -e

kops create -f cluster.yml
kops create -f masters.yml
kops create -f nodes.yml
bash ./secret.sh
