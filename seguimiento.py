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

import os, logging, cgi, urllib, base64

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from base import *

class Modificar_seguimiento(webapp.RequestHandler):
    def get(self, keyp=None):
        try:
            p = Pregunta.get( keyp )
            s = p.get_seguimiento()
            if users.get_current_user() == p.autor: # el autor no puede
                pass
            elif not s: # no hay datos
                s = Seguimiento()
                s.id_pregunta = str( p.key() )
                s.respuestas = p.respuestas
                s.estado = p.estado
                s.usuarios = [ users.get_current_user() ]
                s.put()
                s.borrar_cache()
            elif users.get_current_user() in s.usuarios: # el usuario ya es seguidor
                u = s.usuarios
                u.remove( users.get_current_user() )
                if len( u ) == 0:
                    s.delete()
                else:
                    s.usuarios = u
                    s.put()
                    s.borrar_cache()
            else: # el usuario no es seguidor
                u = s.usuarios
                u.append( users.get_current_user() )
                s.usuarios = u
                s.put()
                s.borrar_cache()
            self.redirect( p.get_link() )
        except:
            self.redirect('/error/503')

def main():
    application = webapp.WSGIApplication( [(r'/seguir/(.*)', Modificar_seguimiento)], debug=DEBUG_FLAG )
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
