#!/usr/bin/env python

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
            e.clickar( self.request.remote_addr )
            comentarios = e.get_comentarios( e.comentarios )
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
                e.actualizar()
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
