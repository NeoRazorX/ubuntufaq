#!/usr/bin/env python

import os
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from base import *

template_values = {
    'respuestas': db.GqlQuery("SELECT * FROM Respuesta ORDER BY fecha DESC").fetch(15),
    'comentarios': db.GqlQuery("SELECT * FROM Comentario ORDER BY fecha DESC").fetch(15)
}

template.register_template_library('filtros_django')
path = os.path.join(os.path.dirname(__file__), 'templates/rss-respuestas.html')

print 'Content-Type: text/xml'
print ''
print template.render(path, template_values)

