#!/bin/bash

arch=`uname`

if [ "$arch" == "Linux" ]
then
  aptitude install -yq python{,-dev}
else
  echo 'Darwin detected, skipping python install.'
fi

pip install --user -r requirements.txt
ansible-playbook -v -i inventory/localhost workstation.yml
