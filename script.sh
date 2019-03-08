#!/bin/bash

# this fails but that is the intent because we want to parse the STDERR hence "|| true"
last_version=$(pip install pentagon==  2>&1 | grep "Could not find" | awk -F',' '{ print $(NF -1) }' | sed s/[[:blank:]]/''/g) || true
pip install --user pentagon==${last_version}
export PATH=$PATH:/home/circleci/.local/bin/pentagon
yes | pentagon start-project migration-test
cd migration-test-infrastructure
export INFRASTRUCTURE_REPO=$(pwd)
cd inventory/default/clusters/production
yes | pentagon add kops.cluster -f vars.yml -o cluster-config
cd $INFRASTRUCTURE_REPO
# faking git config. The repo must have at least one commit for the migration to work
git add . && git -c user.name='fake' -c user.email='fake@email.org' commit -m 'initial commit'
pip install --user -e ~/pentagon
pentagon migrate --yes
