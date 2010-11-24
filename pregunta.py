#!/usr/bin/env python

import cgi, os, math, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from recaptcha.client import captcha
from datetime import datetime
from base import *

class Nueva_pregunta(Pagina):
    def get(self):
        Pagina.get(self)
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = "recaptcha-public-key",
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': 'Ubuntu FAQ - nueva pregunta',
            'descripcion': 'Formulario de creacion de preguntas',
            'tags': 'ubufaq, ubuntu FAQ, problema ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'nueva',
            'captcha': chtml
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/buscar.html')
        self.response.out.write(template.render(path, template_values))

class Preguntar(webapp.RequestHandler):
    def post(self):
        p = Pregunta()
        p.titulo = cgi.escape( self.request.get('titulo') )
        p.contenido = cgi.escape( self.request.get('contenido') )
        p.tags = cgi.escape( self.request.get('tags') )
        
        if users.get_current_user() and self.request.get('titulo') and self.request.get('contenido'):
            p.autor = users.get_current_user()
            p.enviar_email = True
            try:
                p.put()
                self.redirect('/question/' + str( p.key() ))
            except:
                self.redirect('/error/503')
        elif self.request.get('titulo') and self.request.get('contenido'):
            challenge = self.request.get('recaptcha_challenge_field')
            response  = self.request.get('recaptcha_response_field')
            remoteip  = self.request.remote_addr
            cResponse = captcha.submit(
                challenge,
                response,
                "recaptcha-private-key",
                remoteip)
            
            if cResponse.is_valid:
                try:
                    p.put()
                    self.redirect('/question/' + str( p.key() ))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403c')
        else:
            self.redirect('/error/403')

class Detalle_pregunta(Pagina):
    def get(self, id_p=None):
        Pagina.get(self)
        
        try:
            p = Pregunta.get( id_p )
        except:
            p = None
        
        if p:
            # actualizamos las visitas, no pasa nada si no se puede
            if p.ultima_ip != self.request.remote_addr:
                p.ultima_ip = self.request.remote_addr
                p.visitas += 1
                try:
                    p.put()
                except:
                    pass
            
            r = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1 ORDER BY fecha ASC", str(p.key())).fetch(100)
            editar = False
            modificar = False
            
            if (users.get_current_user() and users.get_current_user() == p.autor) or users.is_current_user_admin():
                editar = True
            
            if self.request.get('modificar') and editar:
                modificar = True
            
            # el captcha
            if users.get_current_user():
                chtml = ''
            else:
                chtml = captcha.displayhtml(
                    public_key = "recaptcha-public-key",
                    use_ssl = False,
                    error = None)
            
            template_values = {
                'titulo': p.titulo,
                'descripcion': p.contenido,
                'pregunta': p,
                'tags': 'problema ubuntu, ' + p.tags,
                'respuestas': r,
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario': self.formulario,
                'administrador': users.is_current_user_admin(),
                'editar': editar,
                'modificar': modificar,
                'captcha': chtml,
                'usuario': users.get_current_user()
                }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/pregunta.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')

# solo el autor de la preguna o un administrador puede modificarla
class Modificar_pregunta(webapp.RequestHandler):
    def post(self):
        try:
            p = Pregunta.get( self.request.get('id') )
        except:
            p = None
        
        if p and self.request.get('titulo') and self.request.get('contenido') and self.request.get('tags'):
            if (users.get_current_user() == p.autor) or users.is_current_user_admin():
                try:
                    p.titulo = cgi.escape( self.request.get('titulo') )
                    p.contenido = cgi.escape( self.request.get('contenido') )
                    p.tags = cgi.escape( self.request.get('tags') )
                    p.put()
                    logging.warning("Se ha modificado la pregunta con id: " + self.request.get('id'))
                    self.redirect('/question/' + self.request.get('id'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

# solo el autor de la preguna o un administrador puede modificarla
class Mod_estado_pregunta(webapp.RequestHandler):
    def post(self):
        try:
            p = Pregunta.get( self.request.get('id') )
        except:
            p = None
        
        if p and self.request.get('estado'):
            if (users.get_current_user() == p.autor) or users.is_current_user_admin():
                try:
                    p.estado = int( self.request.get('estado') )
                    p.put()
                    logging.warning("Se ha modificado la pregunta con id: " + self.request.get('id'))
                    self.redirect('/question/' + self.request.get('id'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

class Borrar_pregunta(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id'):
            continuar = True
            try:
                r = Respuesta.all().filter('id_pregunta =', self.request.get('id'))
                db.delete(r)
            except:
                continuar = False
            
            # borramos la pregunta
            if continuar:
                try:
                    p = Pregunta.get( self.request.get('id') )
                    p.delete()
                except:
                    continuar = False
            
            if continuar:
                logging.warning('Se ha eliminado la pregunta con id: ' + self.request.get('id'))
                self.redirect('/')
            else:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Responder(webapp.RequestHandler):
    def post(self):
        fallo = 0
        r = Respuesta()
        r.contenido = cgi.escape( self.request.get('contenido') )
        r.id_pregunta = self.request.get('id_pregunta')
        
        if users.get_current_user() and self.request.get('id_pregunta') and self.request.get('contenido'):
            r.autor = users.get_current_user()
            try:
                r.put()
            except:
                fallo = 2
        elif self.request.get('id_pregunta') and self.request.get('contenido'):
            challenge = self.request.get('recaptcha_challenge_field')
            response = self.request.get('recaptcha_response_field')
            remoteip = self.request.remote_addr
            cResponse = captcha.submit(
                challenge,
                response,
                "recaptcha-private-key",
                remoteip)
            
            if cResponse.is_valid:
                try:
                    r.put()
                except:
                    fallo = 2
            else:
                fallo = 3
        else:
            fallo = 1
        
        if fallo == 0:
            p = Pregunta.get( self.request.get('id_pregunta') )
            p.respuestas = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1", self.request.get('id_pregunta')).count()
            p.fecha = datetime.now()
            try:
                p.put()
                self.redirect('/question/' + self.request.get('id_pregunta'))
            except:
                self.redirect('/error/503')
        elif fallo == 1:
            self.redirect('/error/403')
        elif fallo == 2:
            self.redirect('/error/503')
        elif fallo == 3:
            self.redirect('/error/403c')
        else:
            self.redirect('/error/503')

# solo el autor de la preguna o un administrador puede destacar una respuesta
class Destacar_respuesta(webapp.RequestHandler):
    def get(self):
        try:
            p = Pregunta.get( self.request.get('id') )
            r = Respuesta.get( self.request.get('r') )
        except:
            p = r = None
        
        if p and r and self.request.get('id') and self.request.get('r'):
            if (users.get_current_user() == p.autor) or users.is_current_user_admin():
                try:
                    r.destacada = not(r.destacada)
                    r.put()
                    self.redirect('/question/' + self.request.get('id'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

class Borrar_respuesta(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('r'):
            continuar = True
            try:
                r = Respuesta.get( self.request.get('r') )
                r.delete()
            except:
                continuar = False
            
            # actualizamos la pregunta
            if continuar:
                try:
                    p = Pregunta.get( self.request.get('id') )
                    p.respuestas = Respuesta.all().filter("id_pregunta =", self.request.get('id')).count()
                    p.put()
                except:
                    continuar = False
            
            if continuar:
                logging.warning('Se ha eliminado la respuesta con id: ' + self.request.get('r'))
                self.redirect('/question/' + self.request.get('id'))
            else:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

