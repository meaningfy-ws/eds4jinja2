#!/usr/bin/python3

# __init__.py
# Date:  07/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

__docformat__ = "restructuredtext en"

# The format of the __version__ line is matched by a regex in setup.py and /docs/conf.py
__version__ = "0.1.19"
__date__ = "2020-08-14"

import logging

# hard coding the log level
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
