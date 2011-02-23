#!/usr/bin/env python

import os

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db
from base import *

template_values = {
    'enlaces': db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC LIMIT 25")
}

path = os.path.join(os.path.dirname(__file__), 'templates/pingbacks.html')

print 'Content-Type: text/xml'
print ''
print template.render(path, template_values)

