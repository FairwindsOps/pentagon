
from pentagon import migration
from pentagon.migration import *
from pentagon.component import core, inventory
from pentagon.helpers import merge_dict


class Migration(migration.Migration):
    _starting_version = '2.1.0'
    _ending_version = '2.2.0'

    def run(self):

        for item in self.inventory:

            inventory_path = "inventory/{}".format(item)
            logging.debug('Inventory Path: {}'.format(inventory_path))

            with self.YamlEditor('{}/config/local/vars.yml'.format(inventory_path)) as vars_yml:
                inventory_vars = vars_yml.get_data()

            template_context  = {
                'aws_region': inventory_vars.get('AWS_DEFAULT_REGION'),
                'infrastructure_bucket': inventory_vars.get('INFRASTRUCTURE_BUCKET')
            }

            if os.path.exists("{}/vpc".format(inventory_path)):
                # Move files around
                self.move("{}/vpc".format(inventory_path), "{}/terraform".format(inventory_path))
                self.move("{}/terraform/terraform.tfvars".format(inventory_path), "{}/terraform/aws_vpc.auto.tfvars".format(inventory_path))
                self.move("{}/terraform/variables.tf".format(inventory_path), "{}/terraform/aws_vpc_variables.tf".format(inventory_path))
                self.move("{}/terraform/main.tf".format(inventory_path), "{}/terraform/aws_vpc.tf".format(inventory_path))

                # Mutate files
                aws_vpc_file_content = self.get_file_content("{}/terraform/aws_vpc.tf".format(inventory_path)).split('\n')
                i = aws_vpc_file_content.index("// terraform backend config")
                new_aws_vpc_file_content = \
                    aws_vpc_file_content[0:i-1] + \
                    aws_vpc_file_content[i+9:-1]

                new_aws_vpc_file_content = ('\n').join(new_aws_vpc_file_content[6:-1])
                self.overwrite_file("{}/terraform/aws_vpc.tf".format(inventory_path), new_aws_vpc_file_content)

                # Add new versions of files
                i = inventory.Inventory(merge_dict(template_context, {'cloud': 'aws', 'name': 'default'}))
                i._overwrite = True
                i._destination = "{}/terraform/".format(inventory_path)
                i._add_files('terraform/backend.tf.jinja')
                i._add_files('terraform/Makefile.jinja')
                i._add_files('terraform/provider.tf.jinja')
                i._render_directory_templates()

                logging.warn("####### IMPORTANT: Your s3 backend configuration as changed ######")
                logging.warn("Move your state path in s3:")
                logging.warn("Command example: ")
                logging.warn("aws s3 sync s3://{bucket}/{org}/{old_path}/ s3://{bucket}/{org}/{new_path}/".format(
                    bucket=inventory_vars.get('INFRASTRUCTURE_BUCKET'), 
                    org=inventory_vars.get('org_name'), 
                    old_path='terraform-vpc', 
                    new_path='terraform')
                )
                logging.warn("aws s3 rm s3://{bucket}/{org}/{old_path}/".format(
                    bucket=inventory_vars.get('INFRASTRUCTURE_BUCKET'), 
                    org=inventory_vars.get('org_name'), 
                    old_path='terraform-vpc')
                )

