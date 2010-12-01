#!/usr/bin/env python

import os
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from base import *

template_values = {
    'preguntas': db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(15),
    'enlaces': db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(15)
}

path = os.path.join(os.path.dirname(__file__), 'templates/rss.html')

print 'Content-Type: text/xml'
print ''
print template.render(path, template_values)

