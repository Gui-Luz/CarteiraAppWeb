import sys

project_home = '/var/www/CarteiraAppWeb/'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app as application