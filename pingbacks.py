#!/usr/bin/env python

import os
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from base import *

template_values = {
    'enlaces': db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(25)
}

path = os.path.join(os.path.dirname(__file__), 'templates/pingbacks.html')

print 'Content-Type: text/xml'
print ''
print template.render(path, template_values)

