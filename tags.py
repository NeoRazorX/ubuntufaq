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

import cgi, os, logging, random
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from recaptcha.client import captcha
from base import *

class Detalle_tag(Pagina):
    def get(self, tag=None):
        Pagina.get(self)
        
        template_values = {
                'titulo': 'Ubuntu FAQ: ' + tag,
                'descripcion': 'Páginas relacionadas con ' + tag,
                'tag': tag,
                'tags': 'problema, duda, ayuda, ' + tag,
                'relacionadas': self.paginas_relacionadas( tag ),
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'usuario': users.get_current_user(),
                'error_dominio': self.error_dominio
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/tags.html')
        self.response.out.write(template.render(path, template_values))