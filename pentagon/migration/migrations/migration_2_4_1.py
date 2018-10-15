from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict


class Migration(migration.Migration):
    _starting_version = '2.4.1'
    _ending_version = '2.4.2'

    def run(self):
        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            self.delete("{}/terraform/Makefile".format(inventory_path))

        self.delete('Makefile')
