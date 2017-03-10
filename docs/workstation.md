# Workstation

Here's an example of the steps taken for initial setup, and use of `local-config-init`, for a test client named `testmj`

```
$ mkproject testmj
New python executable in ~/workspace/venvs/testmj/bin/python
Installing setuptools, pip, wheel...done.
virtualenvwrapper.user_scripts creating ~/workspace/venvs/testmj/bin/predeactivate
virtualenvwrapper.user_scripts creating ~/workspace/venvs/testmj/bin/postdeactivate
virtualenvwrapper.user_scripts creating ~/workspace/venvs/testmj/bin/preactivate
virtualenvwrapper.user_scripts creating ~/workspace/venvs/testmj/bin/postactivate
virtualenvwrapper.user_scripts creating ~/workspace/venvs/testmj/bin/get_env_details
To initialize an infrastructure repo from the cookiecutter template, run:

cookiecutter /Users/justin/workspace/cookiecutters/client-infrastructure -o ~/workspace/projects/testmj

After initialization, source environment vars with:

source ~/workspace/projects/testmj/testmj-infrastructure/config/local/vars

Pre-existing infrastructure repositories should be cloned at this stage.
Creating ~/workspace/projects/testmj
Setting project for testmj to ~/workspace/projects/testmj
$ pip install -e ../reactiveops/pentagon
Obtaining file://~/workspace/projects/reactiveops/pentagon
Installing collected packages: pentagon
  Running setup.py develop for pentagon
Successfully installed pentagon
You are using pip version 8.0.2, however version 9.0.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
$ pentagon-startproject  -n testmj-infrastructure
Name is:  testmj-infrastructure
$ cd testmj-infrastructure/config/local/
$ ./local-config-init
ansible.cfg-default -> ansible.cfg created.
ssh_config-default -> ssh_config created.
```
