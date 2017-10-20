from pentagon.component import ComponentBase
import os
import glob
import shutil
import logging
import traceback
import sys
import re

from pentagon.helpers import render_template


class Cluster(ComponentBase):
    _path = os.path.dirname(__file__)
