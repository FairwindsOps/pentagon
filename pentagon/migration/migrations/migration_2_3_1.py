from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict


class Migration(migration.Migration):
    _starting_version = '2.3.1'
    _ending_version = '2.4.0'

    def run(self):
        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            logging.debug(
                'Processing Inventory Item: {}'
                .format(inventory_path)
            )
            with self.YamlEditor('{}/config/local/vars.yml'.format(inventory_path)) as vars_yml:
                vars_yml_dict = vars_yml.get_data()

            logging.info('Found KUBECONFIG in vars.yml = {}'
                         .format(vars_yml_dict.get('KUBECONFIG')))
            logging.info('Found ANSIBLE_CONFIGin vars.yml = {}'
                         .format(vars_yml_dict.get('ANSIBLE_CONFIG')))
            vars_yml_dict['KUBECONFIG'] = '${INFRASTRUCTURE_REPO}/inventory/${INVENTORY}/config/private/kube_config'
            vars_yml_dict['ANSIBLE_CONFIG'] = '${INFRASTRUCTURE_REPO}/inventory/${INVENTORY}/config/private/ansible.cfg'
            logging.info('Changed KUBECONFIG to be {}'
                         .format(vars_yml_dict.get('KUBECONFIG')))
            logging.info('Changed ANSIBLE_CONFIG to be {}'
                         .format(vars_yml_dict.get('ANSIBLE_CONFIG')))

            logging.warn(
                '####### IMPORTANT: Your kube and ansible config paths have changed.')

            vars_yml.write()
