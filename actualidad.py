#!/usr/bin/env python
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
from datetime import datetime
from base import *

class Actualidad(Pagina):
    # muestra los ultimos enlaces
    def get(self, p=0):
        Pagina.get(self)
        
        enlaces_query = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC")
        
        # paginamos
        enlaces, paginas, p_actual = self.paginar(enlaces_query, 20, p)
        datos_paginacion = [paginas, p_actual, '/actualidad/']
        
        template_values = {
            'titulo': 'Actualidad de Ubuntu FAQ',
            'descripcion': 'Noticias, blogs, videos, imagenes y en definitiva toda la actualidad en torno a Ubuntu y Linux en general. Comparte con nosotros!',
            'tags': 'ubufaq, ubuntu faq, noticias ubuntu, actualidad ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'actualidad',
            'enlaces': enlaces,
            'datos_paginacion': datos_paginacion,
            'usuario': users.get_current_user(),
            'error_dominio': self.error_dominio
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/actualidad.html')
        self.response.out.write(template.render(path, template_values))
    
    # crea un nuevo enlace
    def post(self):
        if self.request.get('url') and self.request.get('descripcion'):
            # comprobamos que no se haya introducido anteriormente el enlace
            url = self.request.get('url')
            enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE url = :1", url).fetch(1)
            if enlaces:
                self.redirect('/story/' + str( enlaces[0].key() ))
            else:
                enl = Enlace()
                enl.descripcion = cgi.escape( self.request.get('descripcion').replace("\n", ' ') )
                enl.url = url
                enl.os = self.request.environ['HTTP_USER_AGENT']
                
                if users.get_current_user():
                    if self.request.get('anonimo') != 'on':
                        enl.autor = users.get_current_user()
                    try:
                        enl.put()
                        enl.borrar_cache()
                        self.redirect( enl.get_link() )
                    except:
                        logging.warning('Imposible guardar enlace a: ' + url)
                        self.redirect('/error/503')
                else:
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
                            enl.put()
                            enl.borrar_cache()
                            self.redirect( enl.get_link() )
                        except:
                            logging.warning('Imposible guardar enlace a: ' + url)
                            self.redirect('/error/503')
                    else:
                        self.redirect('/error/403c')
        else:
            self.redirect('/error/403')

class Redir_enlace(webapp.RequestHandler):
    def get(self, id_enlace=None):
        if id_enlace:
            self.redirect('/story/' + id_enlace)
        else:
            self.redirect('/error/404')

class Detalle_enlace(Pagina):
    # devuelve las paginas relacionadas con alguno de los tags del enlace
    def relacionadas(self, cadena):
        tags = cadena.split(', ')
        if len(tags) > 1:
            eleccion = tags[random.randint(0, len( tags ) - 1)]
        elif len(tags) == 1:
            eleccion = tags[0]
        return memcache.get( 'tag_' + eleccion )
    
    # muestra el enlace
    def get(self, id_enlace=None):
        Pagina.get(self)
        
        try:
            e = Enlace.get( id_enlace )
        except:
            e = None
        
        if e:
            # el captcha
            if users.get_current_user():
                chtml = ''
            else:
                chtml = captcha.displayhtml(
                    public_key = RECAPTCHA_PUBLIC_KEY,
                    use_ssl = False,
                    error = None)
            
            if self.request.get('modificar') and users.is_current_user_admin():
                modificar = True
            else:
                modificar = False
            
            template_values = {
                'titulo': e.descripcion + ' - Ubuntu FAQ',
                'descripcion': 'Discusion sobre: ' + e.descripcion,
                'tags': 'ubufaq, ubuntu faq, ' + self.extraer_tags(e.descripcion),
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario': self.formulario,
                'enlace': e,
                'comentarios': e.get_comentarios(self.request.remote_addr),
                'captcha': chtml,
                'relacionadas': self.relacionadas( self.extraer_tags(e.descripcion) ),
                'administrador': users.is_current_user_admin(),
                'modificar': modificar,
                'usuario': users.get_current_user(),
                'error_dominio': self.error_dominio
                }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/enlace.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')
    
    # modifica el enlace
    def post(self):
        if users.is_current_user_admin():
            try:
                e = Enlace.get( self.request.get('id') )
                e.url = self.request.get('url')
                e.descripcion = cgi.escape( self.request.get('descripcion').replace("\n", ' ') )
                if self.request.get('tipo_enlace') in ['youtube', 'vimeo', 'vhtml5', 'imagen', 'deb', 'package', 'texto']:
                    e.tipo_enlace = self.request.get('tipo_enlace')
                else:
                    e.tipo_enlace = None
                e.put()
                e.borrar_cache()
                logging.warning('Se ha modificado el enlace con id: ' + self.request.get('id'))
                self.redirect( e.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Acceder_enlace(webapp.RequestHandler):
    def get(self, id_enlace=None):
        try:
            e = Enlace.get( id_enlace )
            e.get_comentarios(self.request.remote_addr) # contabiliza clic
            self.redirect( e.url )
        except:
            self.redirect('/error/404')

class Hundir_enlace(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id'):
            try:
                e = Enlace.get( self.request.get('id') )
                e.hundir()
                self.redirect('/actualidad')
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Borrar_enlace(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            try:
                Enlace.get( self.request.get('id') ).borrar_todo()
                logging.warning('Se ha borrado el enlace con id: ' + self.request.get('id'))
                self.redirect('/actualidad')
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Comentar(webapp.RequestHandler):
    def post(self):
        c = Comentario()
        c.contenido = cgi.escape( self.request.get('contenido') )
        c.id_enlace = self.request.get('id_enlace')
        c.os = self.request.environ['HTTP_USER_AGENT']
        
        if users.get_current_user() and self.request.get('contenido') and self.request.get('id_enlace'):
            if self.request.get('anonimo') != 'on':
                c.autor = users.get_current_user()
            self.finalizar( c )
        elif self.request.get('contenido') and self.request.get('id_enlace'):
            challenge = self.request.get('recaptcha_challenge_field')
            response = self.request.get('recaptcha_response_field')
            remoteip = self.request.remote_addr
            cResponse = captcha.submit(
                challenge,
                response,
                RECAPTCHA_PRIVATE_KEY,
                remoteip)
            
            if cResponse.is_valid:
                self.finalizar( c )
            else:
                self.redirect('/error/403c')
        else:
            self.redirect('/error/403')
    
    def finalizar(self, comentario):
        if comentario.contenido.strip() == 'Deja un comentario, es gratis!':
            self.redirect('/error/606')
        else:
            try:
                comentario.put()
                e = comentario.get_enlace()
                e.borrar_cache()
                self.redirect( e.get_link() )
            except:
                self.redirect('/error/503')

class Modificar_comentario(webapp.RequestHandler):
    def post(self):
        if users.is_current_user_admin():
            try:
                c = Comentario.get( self.request.get('id_comentario') )
                e = c.get_enlace()
                c.contenido = cgi.escape( self.request.get('contenido') )
                c.put()
                e.borrar_cache()
                logging.warning('Se ha modificado el comentario con id: ' + self.request.get('id_comentario'))
                self.redirect( e.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Borrar_comentario(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('c'):
            try:
                c = Comentario.get( self.request.get('c') )
                e = c.get_enlace()
                c.delete()
                e.borrar_cache()
                logging.warning('Se ha borrado el comentario con id: ' + self.request.get('c'))
                self.redirect( e.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

