from copy import deepcopy

import sys
import traceback

from pentagon import migration
from pentagon.migration import *
import yaml



readme = """

# Migration 2.7.1 -> Unreleased

## This migration:
- removes older artifacts like the `post-kops.sh` if they exist (bug in previous migration caused this to fail)


"""


class Migration(migration.Migration):
    _starting_version = '2.7.1'
    _ending_version = '0.0.0'

    _readme_string = readme

    def run(self):
      for item in self.inventory:
          inventory_path = "inventory/{}".format(item)
          # If there are no clusters, move on.
          if not os.path.isdir('{}/clusters/'.format(inventory_path)):
              continue

          for cluster_item in os.listdir('{}/clusters/'.format(inventory_path)):
              item_path = '{}/clusters/{}'.format(inventory_path, cluster_item)
              # Remove Post Kops if it exists
              try:
                  os.remove("{}/cluster-config/post-kops.sh".format(item_path))
              except OSError, e:
                  if "No such file or directory" in e
                      pass
                  else:
                    raise e

