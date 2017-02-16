# VPN

## Setup

This can be done before or after configuring and deploying your kubernetes cluster(s). It is required to have your VPC setup prior to starting VPN setup.

* Create a key pair `client_name.admin_vpn` in AWS Console and save it in `config/private/`.
  - `chmod 400 <client_name>.admin_vpn
* Update `config/local/ssh_config` to add path to the key created in step 1 (absolute paths only).
* Update `config/local/ansible.cfg` to point to the ssh config above (absolute paths only).
* Edit `default/resources/admin-environment/env.yml`
  - `aws_key_name` : name of the key pair created in step 1
  - `default_ami` : ubuntu trusty. Make sure it is located in correct region, instance type: `hvm:ebs-ssd`
* In the `$INFRASTRUCTURE_REPO` directory, install ansible requirements
  - `ansible-galaxy install -r ansible-requirements.yml`
* Run the VPN playbook
  - `ansible-playbook vpn.yml`
  - Even when all the inputs are correct, sometimes you will need to re-run ansible a couple times to get through all of the steps.


## Usage

The VPN stack will create an instance with the VPN software that you can connect to using a VPN client. On OSX, one possible alternative is Tunnelblick. No matter the client you choose to use, the keys for each of the users will be deposited into the s3 bucket specified in `default/resources/admin-environment/env.yml` before. Download these and keep use them to access your cluster.

