## Setup VirtualEnvWrapper

* Edit `workstation-vars-example.yaml` for your config and move it to `~/.ro/workstation-vars.yaml`

* `cd pentagon`
* `ansible-playbook -v -i inventory/localhost workstation.yml`
* `source ~/.bash_profile`
* Create a new tab in your terminal and if you can run `enable-virtualenvwrapper`, setup is successful.
