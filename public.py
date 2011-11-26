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

import os, logging

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
from preguntas import *
from enlaces import *

class Portada(Pagina):
    def get(self):
        Pagina.get(self)
        mixto = self.sc.get_portada( users.get_current_user() )
        tags = self.get_tags_from_mixto( mixto )
        template_values = {
            'titulo': 'Ubuntu FAQ',
            'descripcion': APP_DESCRIPTION,
            'tags': tags,
            'mixto': mixto,
            'urespuestas': self.sc.get_ultimas_respuestas(),
            'searches': self.sc.get_allsearches(),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'usuario': users.get_current_user(),
            'notis': self.get_notificaciones(),
            'error_dominio': self.error_dominio,
            'stats': self.sc.get_stats()
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/portada.html')
        self.response.out.write( template.render(path, template_values) )

class Populares(Pagina):
    def get(self):
        Pagina.get(self)
        mixto = self.sc.get_populares()
        tags = self.get_tags_from_mixto( mixto )
        template_values = {
            'titulo': 'Populares - Ubuntu FAQ',
            'descripcion': 'Listado de preguntas y noticias populares de Ubuntu FAQ. ' + APP_DESCRIPTION,
            'tags': tags,
            'mixto': mixto,
            'stats': self.sc.get_stats(),
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
            'karmalist': memcache.get('pending-users'),
            'foco': 'ayuda'
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
        if self.request.get('tipo') == 'pregunta':
            foco = 'pregunta'
        elif self.request.get('tipo') == 'enlace':
            foco = 'enlace'
        else:
            foco = 'pensamiento'
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
            'url2': self.request.get('url'),
            'foco': foco
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/nueva.html')
        self.response.out.write(template.render(path, template_values))

class Pagina_buscar(Pagina):
    def get(self, tag=None):
        Pagina.get(self)
        # para corregir fallos de codificación en el tag
        if isinstance(tag, str):
            tag = unicode( urllib.unquote(tag), 'utf-8')
        else:
            tag = unicode( urllib.unquote(tag) )
        template_values = {
                'titulo': 'Ubuntu FAQ: ' + tag,
                'descripcion': u'Páginas relacionadas con ' + tag,
                'tag': tag,
                'tags': 'problema, duda, ayuda, ' + tag,
                'relacionadas': self.sc.paginas_relacionadas(tag, True),
                'alltags': self.sc.get_alltags(),
                'searches': self.sc.get_allsearches(),
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario' : self.formulario,
                'usuario': users.get_current_user(),
                'notis': self.get_notificaciones(),
                'error_dominio': self.error_dominio,
                'foco': 'buscar'
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/search.html')
        self.response.out.write(template.render(path, template_values))
    
    def post(self, ntag=None):
        Pagina.get(self)
        query = urllib.unquote( self.request.get('query') )
        template_values = {
                'titulo': 'Ubuntu FAQ: ' + query,
                'descripcion': u'Resultados de: ' + query,
                'tag': query,
                'buscando': True,
                'tags': 'problema, duda, ayuda, ' + query,
                'relacionadas': self.sc.buscar( query ),
                'searches': self.sc.get_allsearches(),
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario' : self.formulario,
                'usuario': users.get_current_user(),
                'notis': self.get_notificaciones(),
                'error_dominio': self.error_dominio,
                'foco': 'buscar'
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/search.html')
        self.response.out.write(template.render(path, template_values))

class Guardar_voto(Pagina):
    def get(self, tipo='x', keye=None, voto='-1'):
        try:
            if self.request.environ['HTTP_USER_AGENT'].lower().find('googlebot') != -1:
                logging.info('Googlebot!')
                self.redirect('/')
            else:
                if tipo == 'r':
                    elemento = Respuesta.get( keye )
                elif tipo == 'c':
                    elemento = Comentario.get( keye )
                else:
                    elemento = False
                if not elemento: # no hay elemento a votar
                    logging.warning('Elemento no encontrado!')
                    self.redirect('/error/404')
                elif self.request.remote_addr in elemento.ips and self.request.remote_addr != '127.0.0.1': # ya se ha votado desde esta IP
                    logging.info('Voto ya realizado')
                    self.redirect( elemento.get_link() )
                else: # voto válido
                    ips = elemento.ips
                    ips.append( self.request.remote_addr )
                    elemento.ips = ips
                    if voto == '0':
                        elemento.valoracion -= 1
                        logging.info('Voto negativo')
                    elif voto == '1':
                        elemento.valoracion += 1
                        logging.info('Voto positivo')
                    else:
                        logging.info('Voto no válido: ' + str(voto))
                    elemento.put()
                    elemento.borrar_cache()
                    # actualizamos la estadistica
                    stats = self.sc.get_stats()
                    if voto in ['0', '1']:
                        try:
                            stats['votos'] += 1
                        except:
                            stats['votos'] = 1
                        memcache.replace('stats', stats)
                    self.redirect( elemento.get_link() )
        except:
            self.redirect('/error/503')

class Rss(Pagina):
    def get(self):
        template_values = {
            'portada': self.sc.get_portada(),
            'domain': APP_DOMAIN,
            'title': APP_NAME,
            'descripcion': APP_DESCRIPTION
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/rss.html')
        self.response.out.write(template.render(path, template_values))

class Rssr(Pagina):
    def get(self):
        template_values = {
            'respuestas': self.sc.get_ultimas_respuestas(),
            'comentarios': self.sc.get_ultimos_comentarios(),
            'domain': APP_DOMAIN,
            'title': APP_NAME,
            'descripcion': APP_DESCRIPTION
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/rss-respuestas.html')
        self.response.out.write(template.render(path, template_values))

class Sitemap(Pagina):
    def get(self):
        portada = self.sc.get_portada()
        print 'Content-Type: text/xml'
        print ''
        print '<?xml version="1.0" encoding="UTF-8"?>'
        print '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        for p in portada:
            print '<url><loc>' + p['link'] + '</loc><lastmod>' + str(p['fecha']).split(' ')[0] + '</lastmod><changefreq>always</changefreq><priority>0.9</priority></url>'
        print '</urlset>'

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
            'error_dominio': self.error_dominio,
            'foco': 'buscar'
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
                                        (r'/search/(.*)', Pagina_buscar),
                                        (r'/votar/(.*)/(.*)/(.*)', Guardar_voto),
                                        ('/rss', Rss),
                                        ('/rss-respuestas', Rssr),
                                        ('/sitemap', Sitemap),
                                        ('/sitemap.xml', Sitemap),
                                        (r'/error/(.*)', Perror),
                                        ('/.*', Perror),
                                    ],
                                    debug=DEBUG_FLAG)
    webapp.template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

