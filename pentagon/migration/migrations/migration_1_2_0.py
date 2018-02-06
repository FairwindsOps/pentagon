
import pentagon
from pentagon import migration
from collections import OrderedDict
from pentagon.migration import *


class Migration(migration.Migration):
    _starting_version = '1.2.0'
    _ending_version = '2.0.0'

    def run(self):

        # Create inventory directory if it exists
        inventory_dir = '{}/inventory'.format(self._infrastructure_repository)
        if not os.path.isdir(inventory_dir):
            os.mkdir(inventory_dir)

        # Move default
        if os.path.exists('{}/default'.format(self._infrastructure_repository)):
            self.move('default', "inventory/default")

        self.delete('config/local/env-vars.sh')
        if os.path.exists('{}/config'.format(self._infrastructure_repository)):
            self.move('config/', 'inventory/default/config')

        for item in self.inventory:

            inventory_path = "inventory/{}".format(item)
            logging.debug('Inventory Path: {}'.format(inventory_path))

            if os.path.exists('{}/account/vars.yml'.format(self._infrastructure_repository)):
                account_vars_yml = self.YamlEditor('{}/account/vars.yml'.format(inventory_path)).get()
            else:
                account_vars_yml = OrderedDict()

            if os.path.exists('{}/account/vars.sh'.format(self._infrastructure_repository)):
                account_vars_sh = self.get_file_content('{}/account/vars.sh'.format(inventory_path)).get()
                account_vars = OrderedDict()

                for line in account_vars_sh.split('\n'):
                    line = line.replace('export ', '')
                    llist = line.split('=', 1)
                    account_vars[llist[0]] = llist[1]
            else:
                account_vars = OrderedDict()

            config_vars_yml = self.YamlEditor('{}/config/local/vars.yml'.format(inventory_path))
            config_vars_yml.update(account_vars_yml)
            config_vars_yml.update(account_vars)

            config_vars_yml['ANSIBLE_CONFIG'] = '${{INFRASTRUCTURE_REPO}}/inventory/{}/config'.format(item)
            config_vars_yml['KUBECONFIG'] = "${{INFRASTRUCTURE_REPO}}/inventory/{item}/config/private/kubeconfig".format(item=item)

            config_vars_yml.write()
            self.delete('{}/account'.format(inventory_path))

            if os.path.exists("inventory/{item}/config/local/1password.yml".format(item=item)):
                with self.YamlEditor("inventory/{item}/config/local/1password.yml".format(item=item)) as secrets_yml:
                    secrets_yml['path'] = "inventory/{item}/config/private/".format(item=item)
                    secrets_yml.write()

            # fix ansible path vars
            for file in ['vpn.yml', 'destroy.yml']:
                p = "{}/resources/admin-environment/{}".format(inventory_path, file)
                if os.path.exists("{}/{}".format(self._infrastructure_repository, p)):
                    c = self.get_file_content(p)
                    new_c = c.replace('../../account/vars.yml', '../../config/local/vars.yml')
                    self.overwrite_file(p, new_c)

            local_config_init = '''
if [ -z "${{INFRASTRUCTURE_REPO}}" ]; then
  echo "INFRASTRUCTURE_REPO environment variable must be set"
  exit 1
elif [ ! -d "${{INFRASTRUCTURE_REPO}}" ]; then
  echo "${{INFRASTRUCTURE_REPO}} doesn't exist or isn't a directory"
  exit 1
fi

cd "${{INFRASTRUCTURE_REPO}}/inventory/{item}/config/local" || exit 1

for default_file in *-default; do
  out_file="../private/${{default_file//-default}}"
  echo -n "${{default_file}} -> ${{out_file}} "
  if [ -e "${{out_file}}" ]; then
    echo "already exists. skipping."
    continue
  else
    cat "${{default_file}}" | sed -e "s@__INFRA_REPO_PATH__@$INFRASTRUCTURE_REPO@g" > "${{out_file}}"
    echo "created."
  fi
done
'''.format(item=item)

            self.overwrite_file('{}/config/local/local-config-init'.format(inventory_path), local_config_init, True)

            ansible_cfg_default = '''
[defaults]
inventory = $INFRASTRUCTURE_REPO/plugins/inventory
roles_path = $INFRASTRUCTURE_REPO/roles
filter_plugins = $INFRASTRUCTURE_REPO/plugins/filter_plugins
retry_files_save_path = ~/.ansible-retry
hash_behavior = merge

[ssh_connection]
# this needs the path defined without the use of ENV variables
ssh_args = -F __INFRA_REPO_PATH__/inventory/{item}/config/private/ssh_config
'''.format(item=item)
            self.overwrite_file('{}/config/local/ansible.cfg-default'.format(inventory_path), ansible_cfg_default)

            ssh_config_default = '''
# for the kube / kops working instances
Host 172.20.64.* 172.20.65.* 172.20.66.* 172.20.67.* 172.20.68.* 172.20.69.* 172.20.70.* 172.20.71.* 172.20.72.* 172.20.73.* 172.20.74.* 172.20.75.*
  User admin
  IdentityFile __INFRA_REPO_PATH__/inventory/{item}/config/private/working_kube
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null

# for the kube / kops prod instances
Host 172.20.96.* 172.20.97.* 172.20.98.* 172.20.99.* 172.20.100.* 172.20.101.* 172.20.102.* 172.20.103.* 172.20.104.* 172.20.105.* 172.20.106.* 172.20.107.*
  User admin
  IdentityFile __INFRA_REPO_PATH__/inventory/{item}/config/private/production_kube
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null

# for instances in private_working
Host 172.20.48.* 172.20.49.* 172.20.50.* 172.20.51.* 172.20.52.* 172.20.53.* 172.20.54.* 172.20.55.* 172.20.56.* 172.20.57.* 172.20.58.* 172.20.59.*
  User ubuntu
  IdentityFile __INFRA_REPO_PATH__/inventory/{item}/config/private/working_private
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null

# for instances in private_prod
Host 172.20.32.* 172.20.33.* 172.20.34.* 172.20.35.* 172.20.36.* 172.20.37.* 172.20.38.* 172.20.39.* 172.20.40.* 172.20.41.* 172.20.42.* 172.20.43.*
  User ubuntu
  IdentityFile __INFRA_REPO_PATH__/inventory/{item}/config/private/production_private
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null

# for instances in admin
Host 172.20.0.* 172.20.1.* 172.20.2.* 172.20.3.* 172.20.4.* 172.20.5.* 172.20.6.* 172.20.7.* 172.20.8.* 172.20.9.* 172.20.10.* 172.20.11.*
  User ubuntu
  IdentityFile __INFRA_REPO_PATH__/inventory/{item}/config/private/admin_private
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null

# VPN instance
# Replace the '*' with the IP address of the VPN instance
Host *
  User ubuntu
  IdentityFile __INFRA_REPO_PATH__/inventory/{item}/config/private/admin_vpn
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null
'''.format(item=item)
        self.overwrite_file('{}/config/local/ssh_config-default'.format(inventory_path), ssh_config_default)
        # update core

        self.delete('{}/config/local/ansible.cfg'.format(inventory_path))
        self.delete('{}/config/local/ssh_config'.format(inventory_path))
        self.delete('tests')
        self.delete('tasks')
        self.delete('components')
        pentagon.component.core.Core({}).add(self._infrastructure_repository, overwrite=True)
