import oyaml as yaml

from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict


class Migration(migration.Migration):
    _starting_version = '2.4.3'
    _ending_version = '2.5.0'

    def run(self):

        # Remove Orgname from vars.yml
        # Replace org-name with org in all vpn files
        # Remove 'org' arg for vpn role call  in vpn.yml
        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            with self.YamlEditor('{}/config/local/vars.yml'.format(inventory_path)) as vars_yml:
                vars_yml.remove('org-name')
                vars_yml.remove('secrets_bucket')
                vars_yml.write()

            if os.path.exists("{}/resources/admin-environment/".format(inventory_path)):
                with self.YamlEditor("{}/resources/admin-environment/vpn.yml".format(inventory_path)) as vpn_yml:
                    data = vpn_yml.get_data()
                    try:
                        del data[2]['roles'][0]['org']
                    except (KeyError, IndexError) as e:
                        logging.error(e)

                    self.overwrite_file("{}/resources/admin-environment/vpn.yml".format(inventory_path), yaml.safe_dump(data, default_flow_style=False))

                with self.YamlEditor("{}/resources/admin-environment/env.yml".format(inventory_path)) as env_yml:
                    env_yml['env'] = "{{ org }}"
                    env_yml['open_vpn_host'] = "vpn-{{ org }}.{{ canonical_zone }}"
                    env_yml.write()

                with self.YamlEditor("{}/resources/admin-environment/env.yml".format(inventory_path)) as env_yml:
                    data = env_yml.get_data()
                    try:
                        del data['vpn_bucket']
                    except KeyError, e:
                        pass

                    self.overwrite_file("{}/resources/admin-environment/env.yml".format(inventory_path), yaml.safe_dump(data, default_flow_style=False))
