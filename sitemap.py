#!/usr/bin/env python
#
# This file is part of ubuntufaq
# Copyright (C) 2011  Carlos Garcia Gomez  neorazorx@gmail.com
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from datetime import datetime
from base import *

class sitemap:
    def get_preguntas(self):
        preguntas = memcache.get('sitemap_preguntas')
        if preguntas is None:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(50)
            if memcache.add('sitemap_preguntas', preguntas, SITEMAP_CACHE_TIME):
                logging.info('Almacenando sitemap_preguntas en memcache')
            else:
                logging.error("Fallo al rellenar memcache con las preguntas del sitemap")
        else:
            logging.info('Leyendo sitemap_preguntas de memcache')
        return preguntas
    
    def get_enlaces(self):
        enlaces = memcache.get('sitemap_enlaces')
        if enlaces is None:
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(50)
            if memcache.add('sitemap_enlaces', enlaces, SITEMAP_CACHE_TIME):
                logging.info('Almacenando sitemap_enlaces en memcache')
            else:
                logging.error("Fallo al rellenar memcache con los enlaces del sitemap")
        else:
            logging.info('Leyendo sitemap_enlaces de memcache')
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
