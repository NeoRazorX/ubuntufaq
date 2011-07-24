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
        if preguntas is None:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(20)
            if not memcache.add('sitemap_preguntas', preguntas):
                logging.warning("Fallo al rellenar memcache con las preguntas del sitemap")
        else:
            logging.info('Leyendo sitemap_preguntas de memcache')
        return preguntas
    
    def get_enlaces(self):
        enlaces = memcache.get('sitemap_enlaces')
        if enlaces is None:
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(20)
            if not memcache.add('sitemap_enlaces', enlaces):
                logging.warning("Fallo al rellenar memcache con los enlaces del sitemap")
        else:
            logging.info('Leyendo sitemap_enlaces de memcache')
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
