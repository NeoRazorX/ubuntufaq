#!/usr/bin/env python

from google.appengine.ext import db
from base import *

preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(100)
enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(100)

print 'Content-Type: text/xml'
print ''
print '<?xml version="1.0" encoding="UTF-8"?>'
print '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

for p in preguntas:
    print '<url><loc>http://www.ubufaq.com/question/' + str( p.key() ) + '</loc><lastmod>' + str(p.fecha).split(' ')[0] + '</lastmod><changefreq>always</changefreq><priority>0.9</priority></url>'

for e in enlaces:
    print '<url><loc>http://www.ubufaq.com/story/' + str( e.key() ) + '</loc><lastmod>' + str(e.fecha).split(' ')[0] + '</lastmod><changefreq>always</changefreq><priority>0.8</priority></url>'

print '</urlset>'
