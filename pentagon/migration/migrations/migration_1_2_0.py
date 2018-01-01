
from pentagon import migration


class Migration(migration.Migration):
    _starting_version = '1.2.0'
    _ending_version = '1.2.1'

    def run(self):
        self.move('default', 'inventory')
        self.move('config', 'inventory/config')
