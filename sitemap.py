#!/usr/bin/env python

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from datetime import datetime
from base import *

class sitemap:
    def get_preguntas(self):
        preguntas = memcache.get('sitemap_preguntas')
        if preguntas is not None:
            return preguntas
        else:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(100)
            if not memcache.add('sitemap_preguntas', preguntas):
                logging.error("Fallo al rellenar memcache con las preguntas del sitemap")
            return preguntas
    
    def get_enlaces(self):
        enlaces = memcache.get('sitemap_enlaces')
        if enlaces is not None:
            return enlaces
        else:
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(100)
            if not memcache.add('sitemap_enlaces', enlaces):
                logging.error("Fallo al rellenar memcache con los enlaces del sitemap")
            return enlaces
    
    def __init__(self):
        preguntas = self.get_preguntas()
        enlaces = self.get_enlaces()
        
        print 'Content-Type: text/xml'
        print ''
        print '<?xml version="1.0" encoding="UTF-8"?>'
        print '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        print '<url><loc>http://www.ubufaq.com/inicio</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>always</changefreq><priority>0.8</priority></url>'
        print '<url><loc>http://www.ubufaq.com/populares</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>always</changefreq><priority>0.5</priority></url>'
        print '<url><loc>http://www.ubufaq.com/sin-solucionar</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>always</changefreq><priority>0.5</priority></url>'
        print '<url><loc>http://www.ubufaq.com/actualidad</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>always</changefreq><priority>0.8</priority></url>'
        print '<url><loc>http://www.ubufaq.com/images</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>always</changefreq><priority>0.6</priority></url>'
        print '<url><loc>http://www.ubufaq.com/ayuda</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>'
        print '<url><loc>http://www.ubufaq.com/steam4linux</loc><lastmod>' + datetime.today().strftime("%Y-%m-%d") + '</lastmod><changefreq>always</changefreq><priority>0.8</priority></url>'
        
        
        
        for p in preguntas:
            print '<url><loc>http://www.ubufaq.com/question/' + str( p.key() ) + '</loc><lastmod>' + str(p.fecha).split(' ')[0] + '</lastmod><changefreq>always</changefreq><priority>0.9</priority></url>'
        
        for e in enlaces:
            print '<url><loc>http://www.ubufaq.com/story/' + str( e.key() ) + '</loc><lastmod>' + str(e.fecha).split(' ')[0] + '</lastmod><changefreq>always</changefreq><priority>0.8</priority></url>'
        
        print '</urlset>'

if __name__ == "__main__":
    sitemap()
