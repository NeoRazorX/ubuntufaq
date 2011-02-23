#!/usr/bin/env python

import os, logging

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db
from google.appengine.api import memcache
from base import *

class rss:
    def get_preguntas(self):
        preguntas = memcache.get('sitemap_preguntas')
        if preguntas is not None:
            logging.info('Leyendo sitemap_preguntas de memcache')
        else:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(50)
            if not memcache.add('sitemap_preguntas', preguntas, SITEMAP_CACHE_TIME):
                logging.error("Fallo al rellenar memcache con las preguntas del sitemap")
            else:
                logging.info('Almacenando sitemap_preguntas en memcache')
        return preguntas
    
    def get_enlaces(self):
        enlaces = memcache.get('sitemap_enlaces')
        if enlaces is not None:
            logging.info('Leyendo sitemap_enlaces de memcache')
        else:
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(50)
            if not memcache.add('sitemap_enlaces', enlaces, SITEMAP_CACHE_TIME):
                logging.error("Fallo al rellenar memcache con los enlaces del sitemap")
            else:
                logging.info('Almacenando sitemap_enlaces en memcache')
        return enlaces
    
    def __init__(self):
        template_values = {
            'preguntas': self.get_preguntas(),
            'enlaces': self.get_enlaces()
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/rss.html')
        
        print 'Content-Type: text/xml; charset=utf-8'
        print ''
        print template.render(path, template_values).encode('utf-8')

if __name__ == "__main__":
    rss()
