import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'src')))
sys.path.insert(0, os.path.abspath('/srv/supaharris/venv3/lib/python3.5/site-packages/'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
