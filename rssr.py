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
