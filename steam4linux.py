#!/usr/bin/env python

import os, logging, cgi
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime
from base import *

class steam4linux(webapp.RequestHandler):
    def get_comentarios(self):
        comentarios = memcache.get('steam4linux_comentarios')
        if comentarios is not None:
            return comentarios
        else:
            comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha DESC", STEAM_ENLACE_KEY).fetch(50)
            if not memcache.add('steam4linux_comentarios', comentarios, 10):
                logging.error("Fallo al rellenar memcache con los comentarios de steam4linux")
            return comentarios
    
    def get(self):
        template_values = {
            'enlace': Enlace.get( STEAM_ENLACE_KEY ),
            'comentarios': self.get_comentarios(),
            'usuario': users.get_current_user(),
            'url_login': users.create_login_url( self.request.uri ),
            'error': self.request.get('error')
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/steam4linux.html')
        self.response.out.write( template.render(path, template_values) )
    
    def actualizar_enlace(self, id_enlace):
        e = Enlace.get( id_enlace )
        e.comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1", id_enlace).count()
        e.fecha = datetime.now()
        e.put()
    
    def post(self):
        if users.get_current_user() and self.request.get('contenido'):
            c = Comentario()
            c.contenido = cgi.escape( self.request.get('contenido') )
            c.id_enlace = STEAM_ENLACE_KEY
            c.os = self.request.environ['HTTP_USER_AGENT']
            c.autor = users.get_current_user()
            try:
                c.put()
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
