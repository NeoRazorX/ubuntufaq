#!/usr/bin/env python

import cgi, re, random, logging
from google.appengine.ext import db
from google.appengine.api import urlfetch
import feedparser
from base import *

class rsscanner:
    def __init__(self):
        if len( RSS_LIST ) == 1:
            self.leer( RSS_LIST[0] )
        elif len( RSS_LIST ) > 1:
            self.leer( RSS_LIST[ random.randint(0, len( RSS_LIST ) - 1) ] )
    
    def leer(self, rss):
        continuar = False
        
        try:
            result = urlfetch.fetch( rss )
            if result.status_code == 200:
                continuar = True
            else:
                logging.warning("Url no disponible: " + rss)
        except:
            logging.warning("Imposible leer de la url: " + rss)
        
        if continuar:
            logging.info("Leyendo feed: " + rss)
            self.analizar( result.content )
    
    def analizar(self, contenido):
        feed = feedparser.parse( contenido )
        numero = 0
        for entrada in feed.entries:
            enlace = entrada.link
            titulo = entrada.title
            descripcion = entrada.description
            if self.publicar(enlace, titulo, descripcion):
                logging.info("Enlace publicado: " + enlace)
            else:
                logging.info("Enlace descartado: " + enlace)
            if numero < 9:
                numero += 1
            else:
                break
    
    def publicar(self, link, title, description):
        if link != '' and title != '' and description != '':
            # comprobamos que no se haya introducido anteriormente el enlace
            enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE url = :1", link).fetch(1)
            if enlaces:
                return False
            else:
                nuevo = Enlace()
                nuevo.url = link
                nuevo.os = 'rss-scanner.py'
                auxiliar = title + ': ' + self.elimina_html( description.replace("\n", ' ') )
                if len( auxiliar ) < 489:
                    nuevo.descripcion = auxiliar
                else:
                    nuevo.descripcion = auxiliar[:490] + '...'
                if self.filtrar_entrada(auxiliar):
                    nuevo.put()
                    return True
                else:
                    return False
        else:
            logging.warning("Nada que publicar!")
            return False
    
    def filtrar_entrada(self, texto):
        etiquetas = ['ubuntu', 'linux', 'canonical', 'unity', 'gnome', 'kde', 'x.org', 'wayland', 'compiz', 'firefox', 'wine']
        retorno = False
        for tag in etiquetas:
            if texto.lower().find(tag) != -1:
                retorno = True
        return retorno
    
    def elimina_html(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
if __name__ == "__main__":
    rsscanner()

