import logging
import os
import traceback
import jinja2
import oyaml as yaml
from Crypto.PublicKey import RSA
from stat import *
from collections import OrderedDict


def render_template(template_name, template_path, target, context, delete_template=True, overwrite=False):
        """
        Helper function to write out DRY up templating. Accepts template name (string),
        path (string), target directory (string), context (dictionary) and delete_template (boolean)
        Default behavior is to use the key of the dictionary as the template variable names, replace
        them with the value in the tempalate and delete the template if delete_template is
        True
        """

        logging.info("Writing {}".format(target))
        logging.debug("Template Context: {}".format(context))
        logging.debug("Overwrite is {}".format(overwrite))
        if os.path.isfile(target) and overwrite is not True:
            logging.warn("Cowardly refusing to overwrite existing file {}".format(target))
            return False

        logging.debug("Attempting to write {} from template {}/{}".format(target, template_path, template_name))

        template_path = os.path.normpath(template_path)
        template_name = os.path.normpath(template_name)
        template_permissions = os.stat(template_path + '/' + template_name).st_mode

        with open(target, 'w+') as vars_file:
            try:
                template = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path)).get_template(template_name)
                vars_file.write(template.render(context))
            except Exception, e:
                logging.error("Error writing {}. {}".format(target, traceback.print_exc(e)))
                return False

        os.chmod(target, template_permissions)

        if delete_template:
            logging.debug("Removing {}/{}".format(template_path, template_name))
            os.remove("{}/{}".format(template_path, template_name))


def write_yaml_file(filename, d, overwrite=False):
    """ Accepts  filepath,  dictionary. Writes dictionary in yaml to file path, recursively creating path if necessary """
    if not os.path.exists(os.path.dirname(filename)) and overwrite is False:
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    logging.debug("Writing yaml file {}".format(filename))
    logging.debug(d)
    with open(filename,'w+') as f:
        yaml.dump(d, f, default_flow_style=False)


def create_rsa_key(name, path, bits=2048):
    """ creates an ssh key pair. Accepts name, path and bits. Name is the name of the key pair to generate at Path. Bits defaults to 2048 """

    key = RSA.generate(bits)

    private_key = "{}{}".format(path, name)
    public_key = "{}{}.pub".format(path, name)

    with open(private_key, 'w') as content_file:
        os.chmod(private_key, 0600)
        content_file.write(key.exportKey('PEM'))

    pubkey = key.publickey()
    with open(public_key, 'w') as content_file:
        content_file.write(pubkey.exportKey('OpenSSH'))


def merge_dict(d, new_data, clobber=False):
        """ accepts new_data (dict) and clobbber (boolean). Merges dictionary with dictionary 'd'. If clobber is True, overwrites value. Defaults to false """
        for key, value in new_data.items():
            if d.get(key) is None or clobber:
                logging.debug("Setting component data {}: {}".format(key, value))
                d[key] = value
        return d
