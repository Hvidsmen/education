# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u3122635/data/www/iprofpromeducation.pro/education')
sys.path.insert(1, '/var/www/u3122635/data/djangoenv/lib/python3.6/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'education.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()