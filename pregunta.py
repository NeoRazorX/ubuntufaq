#!/usr/bin/env python

import cgi, os, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from recaptcha.client import captcha
from base import *

class Nueva_pregunta(Pagina):
    # crea la pregunta
    def post(self):
        p = Pregunta()
        p.titulo = cgi.escape( self.request.get('titulo') )
        p.contenido = cgi.escape( self.request.get('contenido') )
        p.tags = self.extraer_tags( self.request.get('titulo') + self.request.get('contenido') )
        p.os = self.request.environ['HTTP_USER_AGENT']
        
        if users.get_current_user() and self.request.get('titulo') and self.request.get('contenido'):
            if self.request.get('anonimo') != 'on':
                p.autor = users.get_current_user()
            try:
                p.put()
                p.borrar_cache()
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
                RECAPTCHA_PRIVATE_KEY,
                remoteip)
            
            if cResponse.is_valid:
                try:
                    p.put()
                    p.borrar_cache()
                    self.redirect('/question/' + str( p.key() ))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403c')
        else:
            self.redirect('/error/403')

class Redir_pregunta(Pagina):
    def get(self, id_p=None):
        if id_p:
            self.redirect('/question/' + id_p)
        else:
            self.redirect('/error/404')

class Detalle_pregunta(Pagina):
    # muestra la pregunta
    def get(self, id_p=None):
        Pagina.get(self)
        
        try:
            p = Pregunta.get( id_p )
        except:
            p = None
        
        if p:
            p.visitar( self.request.remote_addr )
            r = p.get_respuestas( p.respuestas )
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
                    public_key = RECAPTCHA_PUBLIC_KEY,
                    use_ssl = False,
                    error = None)
            
            template_values = {
                'titulo': p.titulo + ' - Ubuntu FAQ',
                'descripcion': p.contenido,
                'pregunta': p,
                'tags': 'problema, duda, ayuda, ' + p.tags,
                'respuestas': r,
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario': self.formulario,
                'administrador': users.is_current_user_admin(),
                'editar': editar,
                'modificar': modificar,
                'captcha': chtml,
                'usuario': users.get_current_user(),
                'error_dominio': self.error_dominio
                }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/pregunta.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')
    
    # modifica la pregunta
    def post(self):
        try:
            p = Pregunta.get( self.request.get('id') )
        except:
            p = None
        
        # solo el autor de la preguna o un administrador puede modificarla
        if p and self.request.get('titulo') and self.request.get('contenido') and self.request.get('tags') and self.request.get('estado'):
            if (users.get_current_user() == p.autor) or users.is_current_user_admin():
                try:
                    p.titulo = cgi.escape( self.request.get('titulo') )
                    p.contenido = cgi.escape( self.request.get('contenido') )
                    p.tags = cgi.escape( self.request.get('tags') )
                    p.estado = int( self.request.get('estado') )
                    p.put()
                    p.borrar_cache()
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
                    p.borrar_cache()
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
    def actualizar_pregunta(self, id_pregunta, respuesta):
        p = Pregunta.get( id_pregunta )
        p.actualizar()
        p.borrar_cache()
        
        # cambiamos el estado de la pregunta en funcion de la respuesta
        if respuesta.autor:
            if respuesta.autor == p.autor:
                if respuesta.contenido.lower().find('solucionad') != -1:
                    p.estado = 10
            elif p.estado == 0:
                p.estado = 2
        elif p.estado == 0:
            p.estado = 2
        
        try:
            p.put()
            self.redirect('/question/' + self.request.get('id_pregunta'))
        except:
            self.redirect('/error/503')
    
    def post(self):
        fallo = 0
        r = Respuesta()
        r.contenido = cgi.escape( self.request.get('contenido') )
        r.id_pregunta = self.request.get('id_pregunta')
        r.os = self.request.environ['HTTP_USER_AGENT']
        
        if users.get_current_user() and self.request.get('id_pregunta') and self.request.get('contenido'):
            if self.request.get('anonimo') != 'on':
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
                RECAPTCHA_PRIVATE_KEY,
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
            self.actualizar_pregunta( self.request.get('id_pregunta'), r )
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
        
        if p and r:
            if (users.get_current_user() == p.autor) or users.is_current_user_admin():
                try:
                    r.destacada = not(r.destacada)
                    r.put()
                    p.borrar_cache()
                    self.redirect('/question/' + self.request.get('id'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

# solo el autor de la preguna o un administrador puede destacar una respuesta
class Modificar_respuesta(webapp.RequestHandler):
    def post(self):
        try:
            p = Pregunta.get( self.request.get('id_pregunta') )
            r = Respuesta.get( self.request.get('id_respuesta') )
        except:
            p = r = None
        
        if p and r:
            if users.is_current_user_admin():
                try:
                    r.contenido = cgi.escape( self.request.get('contenido') )
                    r.put()
                    p.borrar_cache()
                    self.redirect('/question/' + self.request.get('id_pregunta'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

class Borrar_respuesta(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('r'):
            try:
                r = Respuesta.get( self.request.get('r') )
                r.delete()
                p = Pregunta.get( self.request.get('id') )
                p.actualizar()
                p.borrar_cache()
                logging.warning('Se ha eliminado la respuesta con id: ' + self.request.get('r'))
                self.redirect('/question/' + self.request.get('id'))
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

