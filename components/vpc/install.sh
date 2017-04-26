#!/bin/bash


#pentagon install-component --name vpn

# echo "hello"
# echo $INFRASTRUCTURE_REPO

rsync -a --exclude *.jinja pentagon-proposal-wc/components/vpc/files/ $INFRASTRUCTURE_REPO/default/vpc/
jinja2 pentagon-proposal-wc/components/vpc/files/terraform.tfvars.jinja $INFRASTRUCTURE_REPO/config/local/vars.yml > $INFRASTRUCTURE_REPO/default/vpc/terraform.tfvars
