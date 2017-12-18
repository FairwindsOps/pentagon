import logging
import os
import traceback
import jinja2
import yaml


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

        logging.debug("Attempting to write {} from template {}{}".format(target, template_path, template_name))

        with open(target, 'w+') as vars_file:
            try:
                template = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.normpath(template_path))).get_template(os.path.normpath(template_name))
                vars_file.write(template.render(context))
            except Exception, e:
                logging.error("Error writing {}. {}".format(target, traceback.print_exc(e)))
                return False

        if delete_template:
            logging.debug("Removing {}/{}".format(template_path, template_name))
            os.remove("{}/{}".format(template_path, template_name))


def write_yaml_file(filename, dict):
    """ Accepts  filepath,  dictionary. Writes dictionary in yaml to file path, recursively creating path if necessary """

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(filename, "w") as f:
        f.write(yaml.safe_dump(dict))
