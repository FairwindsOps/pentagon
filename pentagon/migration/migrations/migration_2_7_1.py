from copy import deepcopy


from pentagon import migration
import yaml

readme = """

# Migration 2.7.1 -> 2.7.2

## This migration:
- adds kubelet flags that were missing in the last migration to take advantage of the audit policy
- made `anonymousAuth: false` default for Kops clusters. This currently conflicts with metricserver version > 3.0.0


## Risks:
- this requires you to roll the cluster
- metrics-server version compatibility 

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

audit_settings = {
    'auditLogPath': '/var/log/kube-apiserver-audit.log',
    'auditLogMaxAge': 10,
    'auditLogMaxBackups': 1,
    'auditLogMaxSize': 100,
    'auditPolicyFile': '/srv/kubernetes/audit.yaml'
}


class Migration(migration.Migration):
    _starting_version = '2.7.1'
    _ending_version = '2.7.2'

    _readme_string = readme

    def run(self):

        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            # If there are no clusters, move on.
            if not os.path.isdir('{}/clusters/'.format(inventory_path)):
                continue

            for cluster_item in os.listdir('{}/clusters/'.format(inventory_path)):
                item_path = '{}/clusters/{}'.format(inventory_path, cluster_item)
                # Is this a kops cluster?

                # There is a small amount of variation here where some cluster config
                # directories are `cluster` and some are `cluster-config`
                # Align these
                
                if os.path.isdir("{}/cluster".format(item_path)):
                    logging.info("Moving {item_path}/cluster to {item_path}/cluster-config".format(item_path))
                    self.move("{}/cluster".format(item_path), "{}/cluster-config".format(item_path))

                if os.path.isdir(item_path) and os.path.exists("{}/cluster-config/kops.sh".format(item_path)):
                    logging.info("Migrating {} {}.".format(item, cluster_item))

                    # Setup cluster spec with aws-iam auth and audit logging
                    if True:
                        cluster_spec_file = "{}/cluster-config/cluster.yml".format(item_path)
                        with open(cluster_spec_file) as yaml_file:
                            cluster_config = yaml.load(yaml_file.read())
                            cluster_spec = cluster_config['spec']

                            if cluster_spec.get('kubelet') is None:
                                cluster_spec['kubelet'] = {}
                            cluster_spec['kubelet']['anonymousAuth'] = False

                            hooks = cluster_spec.get("hooks")
                            if hooks:
                                logging.debug(hooks)
                                for hook in hooks:
                                    hook['manifest'] = literal_unicode(hook['manifest'])

                            for policy_type in cluster_spec.get('additionalPolicies', {}):
                                cluster_spec['additionalPolicies'][policy_type] = literal_unicode(cluster_spec['additionalPolicies'][policy_type])

                            for fa in cluster_spec.get('fileAssets'):
                                if fa.get('content'):
                                    fa['content'] = literal_unicode(fa['content'])

                            kube_api_server = cluster_spec['kubeAPIServer']

                            for setting, value in audit_settings.items():
                                if kube_api_server.get(setting) != value:
                                    kube_api_server[setting] = value

                        with open(cluster_spec_file, 'w') as yaml_file:
                            yaml_file.write(yaml.dump(cluster_config, default_flow_style=False))
