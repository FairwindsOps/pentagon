#!/bin/bash


#pentagon install-component --name vpn

# echo "hello"
# echo "pwd:"
# pwd
COMPONENT_DIR=$1
echo $component_dir
echo $INFRASTRUCTURE_REPO

rsync -a --exclude *.jinja $COMPONENT_DIR/files/ $INFRASTRUCTURE_REPO/default/vpc/
jinja2 $COMPONENT_DIR/files/terraform.tfvars.jinja $INFRASTRUCTURE_REPO/config/local/vars.yml > $INFRASTRUCTURE_REPO/default/vpc/terraform.tfvars
