#!/usr/bin/env python

import os

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db
from base import *

class rssr:
    def __init__(self):
        template_values = {
            'respuestas': db.GqlQuery("SELECT * FROM Respuesta ORDER BY fecha DESC LIMIT 15"),
            'comentarios': db.GqlQuery("SELECT * FROM Comentario ORDER BY fecha DESC LIMIT 15")
        }
        
        template.register_template_library('filters.filtros_django')
        path = os.path.join(os.path.dirname(__file__), 'templates/rss-respuestas.html')
        
        print 'Content-Type: text/xml; charset=utf-8'
        print ''
        print template.render(path, template_values).encode('utf-8')

if __name__ == "__main__":
    rssr()
