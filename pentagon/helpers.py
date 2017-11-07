import logging
import os
import traceback
import jinja2
import yaml


def render_template(template_name, template_path, target, context):
        logging.info("Writing {}".format(target))
        logging.debug("Template Context: {}".format(context))
        if os.path.isfile(target):
            logging.warn("Cowardly refusing to overwrite existing file {}".format(target))
            return False

        with open(target, 'w+') as vars_file:
            try:
                template = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path)).get_template(template_name)
                vars_file.write(template.render(context))
            except Exception, e:
                logging.error("Error writing {}. {}".format(target, traceback.print_exc(e)))
                return False

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
