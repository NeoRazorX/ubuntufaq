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

import cgi, os, urllib, logging

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users, memcache

from recaptcha.client import captcha
from base import *
from pregunta import *
from actualidad import *
from imagenes import *
from tags import *

class Portada(Pagina):
    def mezclar(self):
        preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(12)
        enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(12)
        mixto = []
        p = e = 0
        while p < len(preguntas) or e < len(enlaces):
            if p >= len(preguntas):
                mixto.append({'tipo': enlaces[e].tipo_enlace,
                            'key': enlaces[e].key(),
                            'autor': enlaces[e].autor,
                            'puntos': enlaces[e].puntos,
                            'descripcion': enlaces[e].descripcion,
                            'clicks': enlaces[e].clicks,
                            'creado': enlaces[e].creado,
                            'fecha': enlaces[e].fecha,
                            'comentarios': enlaces[e].comentarios,
                            'link': '/story/' + str(enlaces[e].key()),
                            'tags': enlaces[e].tags})
                e += 1
            elif e >= len(enlaces):
                mixto.append({'tipo': 'pregunta',
                            'key': preguntas[p].key(),
                            'autor': preguntas[p].autor,
                            'puntos': preguntas[p].puntos,
                            'descripcion': preguntas[p].contenido,
                            'clicks': preguntas[p].visitas,
                            'creado': preguntas[p].creado,
                            'fecha': preguntas[p].fecha,
                            'comentarios': preguntas[p].respuestas,
                            'titulo': preguntas[p].titulo,
                            'estado': preguntas[p].estado,
                            'link': '/question/' + str(preguntas[p].key()),
                            'tags': preguntas[p].tags})
                p += 1
            elif preguntas[p].fecha > enlaces[e].fecha:
                mixto.append({'tipo': 'pregunta',
                            'key': preguntas[p].key(),
                            'autor': preguntas[p].autor,
                            'puntos': preguntas[p].puntos,
                            'descripcion': preguntas[p].contenido,
                            'clicks': preguntas[p].visitas,
                            'creado': preguntas[p].creado,
                            'fecha': preguntas[p].fecha,
                            'comentarios': preguntas[p].respuestas,
                            'titulo': preguntas[p].titulo,
                            'estado': preguntas[p].estado,
                            'link': '/question/' + str(preguntas[p].key()),
                            'tags': preguntas[p].tags})
                p += 1
            else:
                mixto.append({'tipo': enlaces[e].tipo_enlace,
                            'key': enlaces[e].key(),
                            'autor': enlaces[e].autor,
                            'puntos': enlaces[e].puntos,
                            'descripcion': enlaces[e].descripcion,
                            'clicks': enlaces[e].clicks,
                            'creado': enlaces[e].creado,
                            'fecha': enlaces[e].fecha,
                            'comentarios': enlaces[e].comentarios,
                            'link': '/story/' + str(enlaces[e].key()),
                            'tags': enlaces[e].tags})
                e += 1
        return mixto
    
    def get_portada(self):
        mixto = memcache.get( 'portada' )
        if mixto is None:
            mixto = self.mezclar()
            if not memcache.add('portada', mixto):
                logging.warning("Fallo almacenando en memcache la portada")
        else:
            logging.info('Leyendo de memcache para la portada')
        return mixto
    
    def get(self):
        Pagina.get(self)
        mixto = self.get_portada()
        tags = self.get_tags_from_mixto( mixto )
        template_values = {
            'titulo': 'Ubuntu FAQ',
            'descripcion': APP_DESCRIPTION,
            'tags': tags,
            'mixto': mixto,
            'urespuestas': self.get_ultimas_respuestas(),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio,
            'stats': memcache.get( 'stats' )
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/portada.html')
        self.response.out.write( template.render(path, template_values) )

class Populares(Pagina):
    def mezclar(self):
        preguntas = db.GqlQuery("SELECT * FROM Pregunta ORDER BY visitas DESC").fetch(15)
        enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY clicks DESC").fetch(15)
        mixto = []
        p = e = 0
        while p < len(preguntas) or e < len(enlaces):
            if p >= len(preguntas):
                mixto.append({'tipo': enlaces[e].tipo_enlace,
                            'key': enlaces[e].key(),
                            'autor': enlaces[e].autor,
                            'puntos': enlaces[e].puntos,
                            'descripcion': enlaces[e].descripcion,
                            'clicks': enlaces[e].clicks,
                            'creado': enlaces[e].creado,
                            'comentarios': enlaces[e].comentarios,
                            'link': '/story/' + str(enlaces[e].key()),
                            'tags': enlaces[e].tags})
                e += 1
            elif e >= len(enlaces):
                mixto.append({'tipo': 'pregunta',
                            'key': preguntas[p].key(),
                            'autor': preguntas[p].autor,
                            'puntos': preguntas[p].puntos,
                            'descripcion': preguntas[p].contenido,
                            'clicks': preguntas[p].visitas,
                            'creado': preguntas[p].creado,
                            'comentarios': preguntas[p].respuestas,
                            'titulo': preguntas[p].titulo,
                            'estado': preguntas[p].estado,
                            'link': '/question/' + str(preguntas[p].key()),
                            'tags': preguntas[p].tags})
                p += 1
            elif preguntas[p].visitas > enlaces[e].clicks:
                mixto.append({'tipo': 'pregunta',
                            'key': preguntas[p].key(),
                            'autor': preguntas[p].autor,
                            'puntos': preguntas[p].puntos,
                            'descripcion': preguntas[p].contenido,
                            'clicks': preguntas[p].visitas,
                            'creado': preguntas[p].creado,
                            'comentarios': preguntas[p].respuestas,
                            'titulo': preguntas[p].titulo,
                            'estado': preguntas[p].estado,
                            'link': '/question/' + str(preguntas[p].key()),
                            'tags': preguntas[p].tags})
                p += 1
            else:
                mixto.append({'tipo': enlaces[e].tipo_enlace,
                            'key': enlaces[e].key(),
                            'autor': enlaces[e].autor,
                            'puntos': enlaces[e].puntos,
                            'descripcion': enlaces[e].descripcion,
                            'clicks': enlaces[e].clicks,
                            'creado': enlaces[e].creado,
                            'comentarios': enlaces[e].comentarios,
                            'link': '/story/' + str(enlaces[e].key()),
                            'tags': enlaces[e].tags})
                e += 1
        return mixto
    
    def get_portada(self):
        mixto = memcache.get( 'populares' )
        if mixto is None:
            mixto = self.mezclar()
            if not memcache.add('populares', mixto):
                logging.warning("Fallo almacenando en memcache populares")
        else:
            logging.info('Leyendo de memcache para populares')
        return mixto
    
    def get(self):
        Pagina.get(self)
        mixto = self.get_portada()
        tags = self.get_tags_from_mixto( mixto )
        template_values = {
            'titulo': 'Populares - Ubuntu FAQ',
            'descripcion': 'Listado de preguntas y noticias populares de Ubuntu FAQ. ' + APP_DESCRIPTION,
            'tags': tags,
            'mixto': mixto,
            'stats': memcache.get( 'stats' ),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/populares.html')
        self.response.out.write( template.render(path, template_values) )

class Ayuda(Pagina):
    def get(self):
        Pagina.get(self)
        template_values = {
            'titulo': 'Ayuda de Ubuntu FAQ',
            'descripcion': u'Sección de ayuda de Ubuntu FAQ. ' + APP_DESCRIPTION,
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'formulario': self.formulario,
            'error_dominio': self.error_dominio,
            'karmalist': memcache.get('pending-users')
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/ayuda.html')
        self.response.out.write(template.render(path, template_values))

class Nueva_publicacion(Pagina):
    def get(self):
        Pagina.get(self)
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': 'Publicar...',
            'descripcion': u'Formulario de publicación de Ubuntu FAQ. ' + APP_DESCRIPTION,
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'formulario': self.formulario,
            'error_dominio': self.error_dominio,
            'captcha': chtml,
            'tipo': self.request.get('tipo'),
            'contenido': self.request.get('contenido'),
            'url2': self.request.get('url')
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/nueva.html')
        self.response.out.write(template.render(path, template_values))

class Perror(Pagina):
    def get(self, cerror='404'):
        Pagina.get(self)
        
        derror = {
            '403': 'Permiso denegado',
            '403c': 'Permiso denegado - error en el captcha',
            '404': u'Página no encontrada en Ubuntu FAQ',
            '503': 'Error en Ubuntu FAQ',
            '606': 'Idiota detectado'
        }
        
        merror = {
            '403': '403 - Permiso denegado',
            '403c': u'<img src="/img/fuuu_face.png" alt="fuuu"/><br/><br/>403 - Permiso denegado: debes repetir el captcha.<br/>Evita los captchas iniciando sesión.',
            '404': u'404 - Página no encontrada en Ubuntu FAQ',
            '503': '<img src="/img/fuuu_face.png" alt="explosi&oacute;n"/><br/><br/>503 - Error en Ubuntu FAQ,<br/>consulta el estado en: http://code.google.com/status/appengine',
            '606': u'<img src="/img/troll_face.png" alt="troll"/><br/><br/>606 - ¿Por qué no pruebas a escribir algo diferente?'
        }
        
        if cerror == '503':
            logging.error( '503' )
        else:
            logging.warning( cerror )
        
        template_values = {
            'titulo': str(cerror) + ' - Ubuntu FAQ',
            'descripcion': derror.get(cerror, 'Error desconocido'),
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'error': merror.get(cerror, 'Error desconocido'),
            'cerror': cerror,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/portada.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/', Portada),
                                        ('/inicio', Todas_preguntas),
                                        ('/preguntas', Todas_preguntas),
                                        (r'/preguntas/(.*)', Todas_preguntas),
                                        ('/populares', Populares),
                                        ('/sin-solucionar', Sin_solucionar),
                                        ('/actualidad', Actualidad),
                                        (r'/actualidad/(.*)', Actualidad),
                                        ('/images', Imagenes),
                                        (r'/images/(.*)', Imagenes),
                                        (r'/p/(.*)', Redir_pregunta),
                                        (r'/question/(.*)', Detalle_pregunta),
                                        ('/nueva', Nueva_publicacion),
                                        ('/add_p', Nueva_pregunta),
                                        ('/mod_p', Detalle_pregunta),
                                        ('/del_p', Borrar_pregunta),
                                        ('/add_r', Responder),
                                        ('/mod_r', Modificar_respuesta),
                                        ('/del_r', Borrar_respuesta),
                                        (r'/e/(.*)', Acceder_enlace),
                                        (r'/de/(.*)', Redir_enlace),
                                        (r'/story/(.*)', Detalle_enlace),
                                        ('/add_e', Actualidad),
                                        ('/mod_e', Detalle_enlace),
                                        ('/hun_e', Hundir_enlace),
                                        ('/del_e', Borrar_enlace),
                                        ('/add_c', Comentar),
                                        ('/mod_c', Modificar_comentario),
                                        ('/del_c', Borrar_comentario),
                                        ('/ayuda', Ayuda),
                                        (r'/error/(.*)', Perror),
                                        ('/.*', Perror),
                                    ],
                                    debug=DEBUG_FLAG)
    webapp.template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

