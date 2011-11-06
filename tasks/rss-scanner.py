#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
            self.leer( random.choice(RSS_LIST) )
        else:
            logging.info('Lista de RSSs vacia!')
    
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
            self.publicar(entrada.link, entrada.title, entrada.description)
            if numero < 4:
                numero += 1
            else:
                break
    
    def publicar(self, link, title, description):
        if link != '' and title != '' and description != '':
            # comprobamos que no se haya introducido anteriormente el enlace
            enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE url = :1", link).fetch(1)
            if enlaces:
                logging.info("Enlace duplicado: " + link)
            else:
                auxiliar = title + ': ' + self.elimina_html( description.replace("\n", ' ') )
                puntos = self.puntuar_entrada(auxiliar)
                if puntos > 1:
                    nuevo = Enlace()
                    nuevo.url = link
                    nuevo.os = 'rss-scanner.py'
                    if len( auxiliar ) < 489:
                        nuevo.descripcion = auxiliar
                    else:
                        nuevo.descripcion = auxiliar[:490] + '...'
                    try:
                        nuevo.get_tags()
                        nuevo.put()
                        logging.info(str(puntos) + " puntos -> enlace publicado: " + link)
                    except:
                        logging.error('Imposible publicar enlace!')
                else:
                    logging.info(str(puntos) + " puntos -> enlace descartado: " + link)
        else:
            logging.warning("Nada que publicar!")
            return False
    
    def puntuar_entrada(self, texto):
        puntos = 0
        for tag in KEYWORD_LIST:
            aux = texto.lower().find(tag)
            if aux > -1:
                if aux < 99:
                    puntos += 3
                elif aux < 249:
                    puntos += 2
                else:
                    puntos += 1
        return puntos
    
    def elimina_html(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
if __name__ == "__main__":
    rsscanner()

