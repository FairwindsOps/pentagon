# VPN

## Setup

This can be done before or after configuring and deploying your kubernetes cluster(s). It is required to have your VPC setup prior to starting VPN setup.

* Review `account/vars.yml` and ensure that `vpc_tag_name`, `org_name`, `canonical_zone` and `vpn_bucket` are set.
* Create a key pair `$client_vpn_YYMMDD`, eg. `hillghost_vpn_20160101` and save it in `config/private/`. `.` is not used as a separator here to prevent confusion if downloading the PEM file. The date is added as a unique identifier for if/when keys are rotated.

```
$ cd config/private
$ keyname="hillghost_vpn_20160101"
$ aws ec2 create-key-pair --key-name $keyname  --query 'KeyMaterial' --output text > ${keyname}.pem
$ chmod 400 ${keyname}.pem
```
[(Creating a key pair)](http://docs.aws.amazon.com/cli/latest/userguide/cli-ec2-keypairs.html#creating-a-key-pair)

* Update `config/local/ssh_config` to add path to the key created in step 1 (absolute paths only).
* Update `config/local/ansible.cfg` to point to the ssh config above (absolute paths only).
* Edit `default/resources/admin-environment/env.yml`
  - `aws_key_name` : name of the key pair created earlier
  - `default_ami` : Ubuntu trusty as of this writing. Make sure it is located in correct region, instance type: `hvm:ebs-ssd`. Use the [Ubuntu AMI locator](https://cloud-images.ubuntu.com/locator/) if needed.
  - Edit other variables as needed. VPN users to be created, aka VPN clients, are contained in the Ansible array, `openvpn_clients`
* If you haven't already, in the `$INFRASTRUCTURE_REPO` directory, install ansible requirements:

```
ansible-galaxy install -r ansible-requirements.yml
```

* Run the VPN playbook:

```
ansible-playbook default/resources/admin-environment/vpn.yml
```

* Even when all the inputs are correct, sometimes you will need to re-run ansible a couple times to get through all of the steps.


## Usage

The VPN playbook will create an instance with OpenVPN software that you can connect to using a VPN client. On OSX, one possible alternative is Tunnelblick. See: [How to connect to access server from OSX](https://openvpn.net/index.php/access-server/docs/admin-guides/183-how-to-connect-to-access-server-from-a-mac.html)


No matter the client you choose to use, the keys for each of the users will be deposited into the s3 bucket specified in `default/resources/admin-environment/env.yml` before. Download these and keep use them to access your cluster.
