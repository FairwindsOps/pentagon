from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict

import re


class Migration(migration.Migration):
    _starting_version = '2.6.0'
    _ending_version = '2.6.1'

    def run(self):
        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            logging.debug(
                'Processing Inventory Item: {}'
                .format(inventory_path)
            )

            # Remove deprecated variables from VPC TF module usage
            aws_vpc_vars_file = "{}/terraform/aws_vpc_variables.tf".format(inventory_path)
            if os.path.exists(aws_vpc_vars_file):
                aws_vpc_vars_file_content = self.get_file_content(aws_vpc_vars_file)
                aws_vpc_vars_file_content = re.sub(r'\n\s*variable "aws_access_key" {}', '', aws_vpc_vars_file_content)
                aws_vpc_vars_file_content = re.sub(r'\n\s*variable "aws_secret_key" {}', '', aws_vpc_vars_file_content)
                self.overwrite_file(aws_vpc_vars_file, aws_vpc_vars_file_content)
                logging.info('Deprecated Terraform VPC module variables removed in {}'.format(item))
