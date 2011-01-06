#!/usr/bin/env python

import os, logging
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from base import *

class rss:
    def get_preguntas(self):
        preguntas = memcache.get('sitemap_preguntas')
        if preguntas is not None:
            return preguntas
        else:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(100)
            if not memcache.add('sitemap_preguntas', preguntas, 6000):
                logging.error("Fallo al rellenar memcache con las preguntas del sitemap")
            return preguntas
    
    def get_enlaces(self):
        enlaces = memcache.get('sitemap_enlaces')
        if enlaces is not None:
            return enlaces
        else:
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(100)
            if not memcache.add('sitemap_enlaces', enlaces, 6000):
                logging.error("Fallo al rellenar memcache con los enlaces del sitemap")
            return enlaces
    
    def __init__(self):
        template_values = {
            'preguntas': self.get_preguntas(),
            'enlaces': self.get_enlaces()
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/rss.html')
        
        print 'Content-Type: text/xml'
        print ''
        print template.render(path, template_values)

if __name__ == "__main__":
    rss()
