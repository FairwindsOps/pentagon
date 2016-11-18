#!/usr/bin/env bash

arch=`uname`

if [ "$arch" == "Darwin" ]
then
  echo 'Darwin detected, skipping python install.'
else
  sudo aptitude install -yq python{,-dev}
fi

pip install --user -r requirements.txt
ansible-playbook -v -i inventory/localhost workstation.yml
