
from pentagon import migration
from pentagon.migration import *


class Migration(migration.Migration):
    _starting_version = '2.0.0'
    _ending_version = '2.1.0'

    def run(self):

        for item in self.inventory:

            inventory_path = "inventory/{}".format(item)
            logging.debug('Inventory Path: {}'.format(inventory_path))

            with self.YamlEditor('{}/config/local/vars.yml'.format(inventory_path)) as vars_yml:
                if not vars_yml.get('HELM_HOME'):
                    vars_yml['HELM_HOME'] = '${INFRASTRUCTURE_REPO}/helm'
                    vars_yml.write()

            self.delete('roles')
