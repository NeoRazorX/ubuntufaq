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

import cgi, os, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from recaptcha.client import captcha
from datetime import datetime
from base import *

class Imagenes(Pagina):
    def get(self, p=0):
        Pagina.get(self)
        
        enlaces_query = db.GqlQuery("SELECT * FROM Enlace WHERE tipo_enlace = 'imagen' ORDER BY fecha DESC")
        
        # paginamos
        imagenes, paginas, p_actual = self.paginar(enlaces_query, 20, p)
        datos_paginacion = [paginas, p_actual, '/images/']
        
        template_values = {
            'titulo': 'Imagenes de Ubuntu FAQ',
            'descripcion': u'Wallpapers, screenshots, fotos e imágenes de toda la actualidad en torno a Ubuntu Linux, comparte con nosotros las tuyas!',
            'tags': 'ubufaq, ubuntu faq, imagenes ubuntu, wallpapers ubuntu, screenshots ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'imagenes',
            'imagenes': imagenes,
            'datos_paginacion': datos_paginacion,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio,
            'stats': memcache.get( 'stats' )
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/imagenes.html')
        self.response.out.write(template.render(path, template_values))
