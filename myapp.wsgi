#!/usr/bin/python
import sys
import logging
from project import app as application


logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/Item-Catalog-App")
