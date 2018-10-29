from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict

import re


class Migration(migration.Migration):
    _starting_version = '2.5.0'
    _ending_version = '2.6.0'

    def run(self):
        for item in self.inventory:
            inventory_path = "inventory/{}".format(item)
            logging.debug(
                'Processing Inventory Item: {}'
                .format(inventory_path)
            )

            # Update version of VPC TF module
            aws_vpc_file = "{}/terraform/aws_vpc.tf".format(inventory_path)
            if os.path.exists(aws_vpc_file):
                aws_vpc_file_content = self.get_file_content(aws_vpc_file)
                aws_vpc_file_content = re.sub(r'terraform-vpc.git\?ref=v\d+\.\d+.\d+', 'terraform-vpc.git?ref=v3.0.0', aws_vpc_file_content)
                aws_vpc_file_content = re.sub(r'\n\s*aws_secret_key\s+=.+', '', aws_vpc_file_content)
                aws_vpc_file_content = re.sub(r'\n\s*aws_access_key\s+=.+', '', aws_vpc_file_content)
                self.overwrite_file(aws_vpc_file, aws_vpc_file_content)
                logging.info('Terraform VPC module updated to 3.0.0 in {}'.format(item))

            # Remove TF AWS provider variables from secrets. No longer referenced directly in VPC module.
            secret_file = "{}/config/private/secrets.yml".format(inventory_path)
            if os.path.exists(secret_file):
                secrets_file_content = self.get_file_content(secret_file)
                original_secrets_content = secrets_file_content
                secrets_file_content = re.sub(r'# Terraform.*\n', '', secrets_file_content)
                secrets_file_content = re.sub(r'TF_VAR_aws_secret_key:.*\n', '', secrets_file_content)
                secrets_file_content = re.sub(r'TF_VAR_aws_access_key:.*\n\n?', '', secrets_file_content)
                self.overwrite_file(secret_file, secrets_file_content)
                
                if original_secrets_content != secrets_file_content:
                    logging.warn("####### IMPORTANT: Secrets file has been updated #######")
                    logging.warn("  Update changed secrets file in 1Password: {}".format(secret_file))
                    logging.warn("  Terraform AWS provider variables removed in VPC module update and no longer needed in secrets.")
