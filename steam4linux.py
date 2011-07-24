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

import os, logging, cgi

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from recaptcha.client import captcha
from base import *

class steam4linux(webapp.RequestHandler):
    def get(self):
        if STEAM_ENLACE_KEY != '':
            e = Enlace.get( STEAM_ENLACE_KEY )
            comentarios = e.get_comentarios(self.request.remote_addr)
            comentarios.reverse()
            
            #captcha
            chtml = captcha.displayhtml(
                public_key = RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None)
            
            template_values = {
                'enlace': e,
                'comentarios': comentarios,
                'usuario': users.get_current_user(),
                'url_login': users.create_login_url( self.request.uri ),
                'error': self.request.get('error'),
                'captcha': chtml
            }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/steam4linux.html')
            self.response.out.write( template.render(path, template_values) )
        else:
            self.redirect('/')
    
    def post(self):
        challenge = self.request.get('recaptcha_challenge_field')
        response  = self.request.get('recaptcha_response_field')
        remoteip  = self.request.remote_addr
        cResponse = captcha.submit(
            challenge,
            response,
            RECAPTCHA_PRIVATE_KEY,
            remoteip)
        
        if cResponse.is_valid and self.request.get('contenido'):
            c = Comentario()
            c.contenido = cgi.escape( self.request.get('contenido') )
            c.id_enlace = STEAM_ENLACE_KEY
            c.os = self.request.environ['HTTP_USER_AGENT']
            try:
                if self.request.get('email'):
                    c.autor = users.User( self.request.get('email') )
                c.put()
                e = Enlace.get( STEAM_ENLACE_KEY )
                e.borrar_cache()
                self.redirect('/steam4linux')
            except:
                self.redirect('/steam4linux?error=503')
        else:
            self.redirect('/steam4linux?error=403')

def main():
    application = webapp.WSGIApplication( [('/steam4linux', steam4linux)], debug=DEBUG_FLAG )
    template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
