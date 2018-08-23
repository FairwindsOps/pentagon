
from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict


class Migration(migration.Migration):
    _starting_version = '2.2.0'
    _ending_version = '2.3.0'

    def run(self):

        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            logging.debug('Inventory Path: {}'.format(inventory_path))
            self.delete('{}/config/local/local-config-init'.format(inventory_path))
            self.delete('{}/terraform/Makefile'.format(inventory_path))
