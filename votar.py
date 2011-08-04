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

class Guardar_voto(webapp.RequestHandler):
    def get(self, keyr=None, voto='-1'):
        try:
            r = Respuesta.get( keyr )
            if not r: # no hay respuesta
                logging.warning('Respuesta no encontrada!')
                self.redirect('/error/404')
            elif self.request.environ['HTTP_USER_AGENT'].lower().find('googlebot') != -1:
                logging.info('Googlebot!')
                p = r.get_pregunta()
                self.redirect(p.get_link() + '#' + str(r.key()))
            elif self.request.remote_addr in r.ips and self.request.remote_addr != '127.0.0.1': # ya se ha votado desde esta IP
                logging.info('Voto ya realizado')
                p = r.get_pregunta()
                self.redirect(p.get_link() + '#' + str(r.key()))
            else: # voto válido
                p = r.get_pregunta()
                ips = r.ips
                ips.append( self.request.remote_addr )
                r.ips = ips
                if voto == '0':
                    r.valoracion -= 1
                    logging.info('Voto negativo')
                elif voto == '1':
                    r.valoracion += 1
                    logging.info('Voto positivo')
                else:
                    logging.info('Voto no válido: ' + str(voto))
                r.put()
                r.borrar_cache()
                self.redirect(p.get_link() + '#' + str(r.key()))
        except:
            self.redirect('/error/503')

def main():
    application = webapp.WSGIApplication( [(r'/votar/(.*)/(.*)', Guardar_voto)], debug=DEBUG_FLAG )
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
