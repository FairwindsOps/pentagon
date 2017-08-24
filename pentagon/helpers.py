import logging
import os
import traceback
import jinja2


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
