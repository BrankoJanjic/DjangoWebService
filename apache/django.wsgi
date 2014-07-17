import os, sys
sys.path.append('/var/www/html')
sys.path.append('/var/www/html/WebService')
os.environ['DJANGO_SETTINGS_MODULE'] = 'WebService.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
