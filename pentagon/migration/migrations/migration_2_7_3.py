from copy import deepcopy


from pentagon import migration
import yaml
import os
import logging

readme = """

# Migration 2.7.2 -> 3.1.0

## This migration:
- adds an updated kops hook to patch docker-runc


## Risks:
- this requires you to roll the cluster

## Follow up tasks:
- roll the cluster

"""

# Magic to make block formatting in yaml.dump work as expected


class folded_unicode(unicode):
    pass


class literal_unicode(unicode):
    pass


def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)
# https://stackoverflow.com/questions/6432605/any-yaml-libraries-in-python-that-support-dumping-of-long-strings-as-block-liter

runCHookContents = """
name: patch-runc
before:
- docker.service
manifest: |
  Type=oneshot
  ExecStart=/bin/bash -c "wget https://artifacts.reactiveops.com/runc-cve/releases/download/CVE-2019-5736-build2/runc-v17.03.2-amd64 && chattr -i /usr/bin/docker-runc && mv runc-v17.03.2-amd64 /usr/bin/docker-runc && chmod +x /usr/bin/docker-runc && docker-runc --version && echo done || sudo shutdown now 'Patching docker-runc failed'"
  ExecStartPost=/bin/bash -c "docker-runc --version | grep -q ae16ac34cda712253fdf199632fd6b5ec5645e27 || sudo shutdown now"
roles:
- Node
- Master
"""

runCHook = yaml.load(runCHookContents)
runCHook['manifest'] = literal_unicode(runCHook['manifest'])

class Migration(migration.Migration):
    _starting_version = '2.7.2'
    _ending_version = '3.1.0'

    _readme_string = readme

    def run(self):

        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            # If there are no clusters, move on.
            if not os.path.isdir('{}/clusters/'.format(inventory_path)):
                continue

            for cluster_item in os.listdir('{}/clusters/'.format(inventory_path)):
                item_path = '{}/clusters/{}'.format(inventory_path, cluster_item)

                if os.path.isdir(item_path) and os.path.exists("{}/cluster-config/cluster.yml".format(item_path)):
                    logging.info("Migrating {} {}.".format(item, cluster_item))

                    # Setup cluster spec with patch-runc hook
                    if True:
                        cluster_spec_file = "{}/cluster-config/cluster.yml".format(item_path)
                        with open(cluster_spec_file) as yaml_file:
                            cluster_config = yaml.load(yaml_file.read())
                            cluster_spec = cluster_config['spec']

                            for policy_type in cluster_spec.get('additionalPolicies', {}):
                                cluster_spec['additionalPolicies'][policy_type] = literal_unicode(cluster_spec['additionalPolicies'][policy_type])

                            for fa in cluster_spec.get('fileAssets'):
                                if fa.get('content'):
                                    fa['content'] = literal_unicode(fa['content'])

                            hooks = cluster_spec.get("hooks")
                            runCHookIndex = None
                            if hooks:
                                logging.debug(hooks)
                                for index, hook in enumerate(hooks):
                                    hook['manifest'] = literal_unicode(hook['manifest'])
                                    if hook['name'] == 'patch-runc':
                                        logging.info("Found patch-runc hook at index %s", index)
                                        runCHookIndex = index
                                if runCHookIndex:
                                    hooks[runCHookIndex] = runCHook
                                else:
                                    hooks.append(runCHook)
                            else:
                                cluster_spec["hooks"] = []
                                cluster_spec["hooks"].append(runCHook)


                        with open(cluster_spec_file, 'w') as yaml_file:
                            yaml_file.write(yaml.dump(cluster_config, default_flow_style=False))
