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
            'descripcion': u'Noticias, blogs, vídeos, imágenes y en definitiva toda la actualidad en torno a Ubuntu y Linux en general. Comparte con nosotros!',
            'tags': 'ubufaq, ubuntu faq, noticias ubuntu, actualidad ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'actualidad',
            'enlaces': enlaces,
            'datos_paginacion': datos_paginacion,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio,
            'stats': self.sc.get_stats(),
            'foco': 'enlace'
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/actualidad.html')
        self.response.out.write(template.render(path, template_values))
    
    # crea un nuevo enlace
    def post(self):
        if self.request.get('descripcion'):
            redirigir = False
            # comprobamos que no se haya introducido anteriormente el enlace
            url = cgi.escape(self.request.get('url'), True)
            if url != '':
                enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE url = :1", url).fetch(1)
                if enlaces:
                    redirigir = enlaces[0].get_link()
            if redirigir:
                self.redirect( redirigir )
            else:
                enl = Enlace()
                enl.descripcion = cgi.escape(self.request.get('descripcion')[:450].replace("\n", ' '), True)
                if url != '':
                    enl.url = url
                enl.os = self.request.environ['HTTP_USER_AGENT']
                if users.get_current_user():
                    if self.request.get('anonimo') != 'on':
                        enl.autor = users.get_current_user()
                    try:
                        enl.nuevo( self.sc.get_alltags() )
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
                            enl.nuevo()
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
    def get(self, id_enlace=None):
        Pagina.get(self)
        e = self.sc.get_enlace(id_enlace, self.request.remote_addr)
        if e:
            editar = False
            modificar = False
            if (users.get_current_user() and users.get_current_user() == e.autor) or users.is_current_user_admin():
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
                'titulo': e.descripcion + ' - Ubuntu FAQ',
                'descripcion': u'Discusión sobre: ' + e.descripcion,
                'tags': e.tags,
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario': self.formulario,
                'enlace': e,
                'comentarios': self.sc.get_comentarios_de(id_enlace),
                'captcha': chtml,
                'relacionadas': self.sc.paginas_relacionadas( e.tags ),
                'administrador': users.is_current_user_admin(),
                'editar': editar,
                'modificar': modificar,
                'usuario': users.get_current_user(),
                'notis': self.get_notificaciones(),
                'error_dominio': self.error_dominio,
                'foco': 'enlace'
            }
            path = os.path.join(os.path.dirname(__file__), 'templates/enlace.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')
    
    # modifica el enlace
    def post(self):
        e = self.sc.get_enlace( self.request.get('id') )
        if e and ((users.get_current_user() and users.get_current_user() == e.autor) or users.is_current_user_admin()):
            try:
                e.url = cgi.escape(self.request.get('url'), True)
                e.descripcion = cgi.escape(self.request.get('descripcion').replace("\n", ' '), True)
                e.tags = cgi.escape(self.request.get('tags'), True)
                if self.request.get('tipo_enlace') in ['youtube', 'vimeo', 'vhtml5', 'imagen', 'deb', 'package', 'texto']:
                    e.tipo_enlace = self.request.get('tipo_enlace')
                else:
                    e.tipo_enlace = None
                e.put()
                logging.info('Se ha modificado el enlace: ' + e.get_link())
                self.sc.borrar_cache_enlace( self.request.get('id') )
                self.redirect( e.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Acceder_enlace(Pagina):
    def get(self, id_enlace=None):
        try:
            e = self.sc.get_enlace(id_enlace, self.request.remote_addr)
            self.redirect( e.url )
        except:
            self.redirect('/error/404')

class Hundir_enlace(Pagina):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id'):
            e = self.sc.get_enlace( self.request.get('id') )
            if e:
                e.hundir()
                self.sc.borrar_cache( self.request.get('id') )
                self.redirect('/')
            else:
                self.redirect('/error/404')
        else:
            self.redirect('/error/403')

class Borrar_enlace(Pagina):
    def get(self):
        if users.is_current_user_admin():
            e = self.sc.get_enlace( self.request.get('id') )
            if e:
                try:
                    e.borrar_todo()
                    self.sc.borrar_cache_enlace( self.request.get('id') )
                    logging.warning('Se ha borrado el enlace con id: ' + self.request.get('id'))
                    self.redirect('/')
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/404')
        else:
            self.redirect('/error/403')

class Comentar(Pagina):
    def post(self):
        c = Comentario()
        c.contenido = cgi.escape(self.request.get('contenido'), True)
        c.id_enlace = self.request.get('id_enlace')
        c.os = self.request.environ['HTTP_USER_AGENT']
        c.ips = [self.request.remote_addr]
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
        if comentario.contenido.strip() == '':
            self.redirect('/error/606')
        else:
            try:
                comentario.put()
                e = self.sc.get_enlace(comentario.id_enlace)
                if e:
                    e.actualizar()
                    self.sc.borrar_cache_enlace(comentario.id_enlace)
                self.redirect( comentario.get_link() )
            except:
                self.redirect('/error/503')

class Modificar_comentario(webapp.RequestHandler):
    def post(self):
        if users.is_current_user_admin():
            try:
                c = Comentario.get( self.request.get('id_comentario') )
                c.contenido = cgi.escape(self.request.get('contenido'), True)
                c.put()
                c.borrar_cache()
                self.redirect( c.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Borrar_comentario(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('c'):
            try:
                c = Comentario.get( self.request.get('c') )
                c.delete()
                c.borrar_cache()
                logging.warning('Se ha borrado el comentario con id: ' + self.request.get('c'))
                self.redirect( c.get_link() )
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

