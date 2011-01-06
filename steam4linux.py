#!/usr/bin/env python

import os, logging, cgi
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users, memcache
from recaptcha.client import captcha
from datetime import datetime
from base import *

class steam4linux(webapp.RequestHandler):
    def get_enlace(self):
        e = Enlace.get( STEAM_ENLACE_KEY )
        
        # actualizamos los clicks, no pasa nada si no podemos
        if e.ultima_ip != self.request.remote_addr:
            e.ultima_ip = self.request.remote_addr
            e.clicks += 1
            try:
                e.put()
            except:
                pass
        return e
    
    def get_comentarios(self):
        comentarios = memcache.get('steam4linux')
        if comentarios is not None:
            return comentarios
        else:
            comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha DESC", STEAM_ENLACE_KEY).fetch(50)
            if not memcache.add('steam4linux', comentarios):
                logging.error("Fallo al rellenar memcache con los comentarios de steam4linux")
            return comentarios
    
    def get(self):
        if STEAM_ENLACE_KEY != '':
            #captcha
            chtml = captcha.displayhtml(
                public_key = RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None)
            
            template_values = {
                'enlace': self.get_enlace(),
                'comentarios': self.get_comentarios(),
                'usuario': users.get_current_user(),
                'url_login': users.create_login_url( self.request.uri ),
                'error': self.request.get('error'),
                'captcha': chtml
            }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/steam4linux.html')
            self.response.out.write( template.render(path, template_values) )
        else:
            self.redirect('/')
    
    def actualizar_enlace(self, id_enlace):
        e = Enlace.get( id_enlace )
        e.comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1", id_enlace).count()
        e.fecha = datetime.now()
        e.put()
    
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
                memcache.delete( STEAM_ENLACE_KEY )
                memcache.delete('steam4linux')
                self.actualizar_enlace( STEAM_ENLACE_KEY )
                self.redirect('/steam4linux')
            except:
                self.redirect('/steam4linux?error=503')
        else:
            self.redirect('/steam4linux?error=403')

def main():
    application = webapp.WSGIApplication( [('/steam4linux', steam4linux)], debug=DEBUG_FLAG )
    template.register_template_library('filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
