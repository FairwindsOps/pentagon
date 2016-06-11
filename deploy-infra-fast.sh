#!/bin/bash

# with --delete:
# rsync -e "ssh -F $INFRASTRUCTURE_REPO/config/local/ssh_config" -avz --exclude .git --exclude .terraform --delete $INFRASTRUCTURE_REPO/ 10.10.12.69:/opt/omnia/infrastructure/

rsync -e "ssh -F $INFRASTRUCTURE_REPO/config/local/ssh_config" -av --exclude .git --exclude .terraform $INFRASTRUCTURE_REPO/ 10.10.12.69:/opt/omnia/infrastructure/|grep -E -v 'bytes/sec|speedup is|building file list'
rsync -e "ssh -F $INFRASTRUCTURE_REPO/config/local/ssh_config" -avq --exclude .git $INFRASTRUCTURE_REPO/../roles/ 10.10.12.69:/opt/omnia/infrastructure/roles/ |grep -E -v 'bytes/sec|speedup is|building file list'
