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

# clase para listar las preguntas
class Todas_preguntas(Pagina):
    def get(self, p=0):
        Pagina.get(self)
        
        # paginamos
        p_query = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC")
        preguntas, paginas, p_actual = self.paginar(p_query, 20, p)
        datos_paginacion = [paginas, p_actual, '/preguntas/']
        
        template_values = {
            'titulo': 'Todas la preguntas de Ubuntu FAQ',
            'descripcion': 'Todas la preguntas de Ubuntu FAQ. ' + APP_DESCRIPTION,
            'tags': self.get_tags_from_list( preguntas ),
            'preguntas': preguntas,
            'datos_paginacion': datos_paginacion,
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'formulario' : self.formulario,
            'error_dominio': self.error_dominio,
            'stats': memcache.get( 'stats' )
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/preguntas.html')
        self.response.out.write( template.render(path, template_values) )

class Sin_solucionar(Pagina):
    def get_preguntas(self):
        preguntas = memcache.get('sin-solucionar')
        if preguntas is None:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE estado < 10 ORDER BY estado ASC").fetch(100)
            if memcache.add('sin-solucionar', preguntas):
                logging.info('Almacenando sin-solucionar en memcache')
            else:
                logging.error("Fallo al rellenar memcache con las preguntas de sin-solucionar")
        else:
            logging.info('Leyendo sin-solucionar de memcache')
        return preguntas
    
    def get(self, p=0):
        Pagina.get(self)
        preguntas = self.get_preguntas()
        
        template_values = {
            'titulo': 'Ubuntu FAQ - sin solucionar',
            'descripcion': 'Listado de preguntas sin solucionar de Ubuntu FAQ. ' + APP_DESCRIPTION,
            'tags': self.get_tags_from_list( preguntas ),
            'preguntas': preguntas,
            'respuestas': self.get_ultimas_respuestas(),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/sin-solucionar.html')
        self.response.out.write( template.render(path, template_values) )

class Nueva_pregunta(Pagina):
    # crea la pregunta
    def post(self):
        p = Pregunta()
        p.titulo = cgi.escape(self.request.get('titulo'), True)
        p.contenido = cgi.escape(self.request.get('contenido'), True)
        p.tags = self.extraer_tags( self.request.get('titulo') + self.request.get('contenido') )
        p.os = self.request.environ['HTTP_USER_AGENT']
        
        if users.get_current_user() and self.request.get('titulo') and self.request.get('contenido'):
            if self.request.get('anonimo') != 'on':
                p.autor = users.get_current_user()
            try:
                p.put()
                p.borrar_cache()
                self.redirect( p.get_link() )
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
                    self.redirect( p.get_link() )
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
    def get(self, id_p=None):
        Pagina.get(self)
        
        try:
            p = Pregunta.get( id_p )
        except:
            p = None
        
        if p:
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
                'titulo': p.titulo + ' [ ' + p.get_estado() + ' ]',
                'descripcion': p.contenido,
                'pregunta': p,
                'tags': 'problema, duda, ayuda, ' + p.tags,
                'respuestas': p.get_respuestas(self.request.remote_addr),
                'relacionadas': self.paginas_relacionadas( p.tags ),
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario': self.formulario,
                'administrador': users.is_current_user_admin(),
                'editar': editar,
                'modificar': modificar,
                'captcha': chtml,
                'usuario': users.get_current_user(),
                'notis': self.get_notificaciones(),
                'error_dominio': self.error_dominio,
                'es_seguidor': p.es_seguidor( users.get_current_user() )
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
                    p.titulo = cgi.escape(self.request.get('titulo'), True)
                    p.contenido = cgi.escape(self.request.get('contenido'), True)
                    p.tags = cgi.escape(self.request.get('tags'), True)
                    n_estado = int( self.request.get('estado') )
                    if n_estado == 10 and p.estado != n_estado:
                        p.marcar_solucionada()
                    elif n_estado == 11 and p.estado != n_estado:
                        p.marcar_pendiente()
                    p.estado = n_estado
                    p.put()
                    p.borrar_cache()
                    logging.info("Se ha modificado la pregunta con id: " + self.request.get('id'))
                    self.redirect( p.get_link() )
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

class Borrar_pregunta(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id'):
            try:
                Pregunta.get( self.request.get('id') ).borrar_todo()
                logging.warning('Se ha eliminado la pregunta con id: ' + self.request.get('id'))
                self.redirect('/')
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Responder(webapp.RequestHandler):
    def post(self):
        fallo = 0
        r = Respuesta()
        r.contenido = cgi.escape(self.request.get('contenido'), True)
        r.id_pregunta = self.request.get('id_pregunta')
        r.os = self.request.environ['HTTP_USER_AGENT']
        r.ips = [self.request.remote_addr]
        
        if users.get_current_user() and self.request.get('id_pregunta') and self.request.get('contenido'):
            if self.request.get('anonimo') != 'on':
                r.autor = users.get_current_user()
            self.finalizar( r )
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
                self.finalizar( r )
            else:
                self.redirect('/error/403c')
        else:
            self.redirect('/error/403')
    
    def finalizar(self, respuesta):
        if respuesta.contenido.strip() == '':
            self.redirect('/error/606')
        else:
            try:
                respuesta.put()
                p = respuesta.get_pregunta()
                p.actualizar( respuesta )
                self.redirect(p.get_link() + '#' + str(respuesta.key()))
            except:
                self.redirect('/error/503')

# solo el autor de la preguna o un administrador puede destacar una respuesta
class Modificar_respuesta(webapp.RequestHandler):
    def post(self):
        if users.is_current_user_admin():
            try:
                r = Respuesta.get( self.request.get('id_respuesta') )
                p = r.get_pregunta()
                r.contenido = cgi.escape(self.request.get('contenido'), True)
                r.put()
                p.borrar_cache()
                self.redirect( p.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Borrar_respuesta(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('r'):
            try:
                r = Respuesta.get( self.request.get('r') )
                p = r.get_pregunta()
                r.delete()
                p.borrar_cache()
                logging.warning('Se ha eliminado la respuesta con id: ' + self.request.get('r'))
                self.redirect( p.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

