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
                            'link': '/story/' + str(enlaces[e].key())})
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
                            'link': '/question/' + str(preguntas[p].key())})
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
                            'link': '/question/' + str(preguntas[p].key())})
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
                            'link': '/story/' + str(enlaces[e].key())})
                e += 1
        return mixto
    
    def get_portada(self):
        mixto = memcache.get( 'portada' )
        if mixto is None:
            mixto = self.mezclar()
            if memcache.add('portada', mixto):
                logging.info('Almacenando en memcache la portada')
            else:
                logging.error("Fallo almacenando en memcache la portada")
        else:
            logging.info('Leyendo de memcache para la portada')
        return mixto
    
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
            'titulo': 'Ubuntu FAQ - portada',
            'descripcion': 'Soluciones rapidas para tus problemas con Ubuntu, Kubuntu, Xubuntu, Lubuntu, y linux en general, asi como noticias, videos, wallpapers y enlaces de interes.',
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'mixto': self.get_portada(),
            'urespuestas': self.get_ultimas_respuestas(),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'captcha': chtml,
            'usuario': users.get_current_user(),
            'vista': 'portada',
            'error_dominio': self.error_dominio
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/portada.html')
        self.response.out.write( template.render(path, template_values) )

# clase para listar las preguntas
class Indice(Pagina):
    def get(self, p=0, vista='inicio'):
        Pagina.get(self)
        
        # paginamos
        p_query = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC")
        preguntas, paginas, p_actual = self.paginar(p_query, 20, p)
        datos_paginacion = [paginas, p_actual, '/preguntas/']
        
        template_values = {
            'titulo': 'Ubuntu FAQ - ' + vista,
            'descripcion': vista + ' - soluciones rapidas para tus problemas con Ubuntu, Kubuntu, Xubuntu, Lubuntu, y linux en general, asi como noticias, videos, wallpapers y enlaces de interes.',
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'preguntas': preguntas,
            'datos_paginacion': datos_paginacion,
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'vista': 'preguntas',
            'error_dominio': self.error_dominio
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/preguntas.html')
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
                            'link': '/story/' + str(enlaces[e].key())})
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
                            'link': '/question/' + str(preguntas[p].key())})
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
                            'link': '/question/' + str(preguntas[p].key())})
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
                            'link': '/story/' + str(enlaces[e].key())})
                e += 1
        return mixto
    
    def get_portada(self):
        mixto = memcache.get( 'populares' )
        if mixto is None:
            mixto = self.mezclar()
            if memcache.add('populares', mixto):
                logging.info('Almacenando en memcache populares')
            else:
                logging.error("Fallo almacenando en memcache populares")
        else:
            logging.info('Leyendo de memcache para populares')
        return mixto
    
    def get_stats(self):
        return memcache.get( 'stats' )
    
    def get(self):
        Pagina.get(self)
        
        template_values = {
            'titulo': 'Ubuntu FAQ - populares',
            'descripcion': 'Listado de preguntas y noticias populares de Ubuntu FAQ. Soluciones rapidas para tus problemas con Ubuntu, Kubuntu, Xubuntu, Lubuntu, y linux en general, asi como noticias, videos, wallpapers y enlaces de interes.',
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'mixto': self.get_portada(),
            'stats': self.get_stats(),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'usuario': users.get_current_user(),
            'vista': 'populares',
            'error_dominio': self.error_dominio
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/populares.html')
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
        
        template_values = {
            'titulo': 'Ubuntu FAQ - sin solucionar',
            'descripcion': 'Listado de preguntas sin solucionar de Ubuntu FAQ. Soluciones rapidas para tus problemas con Ubuntu, Kubuntu, Xubuntu, Lubuntu, y linux en general, asi como noticias, videos, wallpapers y enlaces de interes.',
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'preguntas': self.get_preguntas(),
            'respuestas': self.get_ultimas_respuestas(),
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'usuario': users.get_current_user(),
            'vista': 'sin-solucionar',
            'error_dominio': self.error_dominio
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/sin-solucionar.html')
        self.response.out.write( template.render(path, template_values) )

class Ayuda(Pagina):
    def get(self):
        Pagina.get(self)
        
        template_values = {
            'titulo': 'Ayuda de Ubuntu FAQ',
            'descripcion': 'Seccion de ayuda de Ubuntu FAQ. Soluciones rapidas para tus problemas con Ubuntu, Kubuntu, Xubuntu, Lubuntu, y linux en general, asi como noticias, videos, wallpapers y enlaces de interes.',
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'ayuda',
            'error_dominio': self.error_dominio
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/ayuda.html')
        self.response.out.write(template.render(path, template_values))

class Detalle_usuario(Pagina):
    def get(self, email=None):
        Pagina.get(self)
        continuar = False
        numreg = 10
        
        if email:
            try:
                usuario = users.User( urllib.unquote( email ) )
                p = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(numreg)
                r = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(numreg)
                e = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(numreg)
                c = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(numreg)
                continuar = True
            except:
                pass
        
        if continuar:
            if usuario == users.get_current_user():
                vista = 'mi-perfil'
            else:
                vista = ''
            
            karma = 0
            if p:
                for col in p:
                    karma = max(col.puntos, karma)
            elif r:
                for col in r:
                    karma = max(col.puntos, karma)
            elif e:
                for col in e:
                    karma = max(col.puntos, karma)
            elif c:
                for col in c:
                    karma = max(col.puntos, karma)
            
            template_values = {
                'titulo': 'Ubuntu FAQ - perfil de ' + str(usuario),
                'descripcion': 'Resumen del historial del usuario ' + str(usuario) + ' en Ubuntu FAQ',
                'preguntas': p,
                'respuestas': r,
                'enlaces': e,
                'comentarios': c,
                'usuario': usuario,
                'karma': karma,
                'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot, ' + str(usuario),
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario' : self.formulario,
                'vista': vista,
                'error_dominio': self.error_dominio
                }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/usuario.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')

class Perror(Pagina):
    def get(self, cerror='404'):
        Pagina.get(self)
        
        derror = {
            '403': 'Permiso denegado',
            '403c': 'Permiso denegado - error en el captcha',
            '404': 'Pagina no encontrada en Ubuntu FAQ',
            '503': 'Error en Ubuntu FAQ',
            '606': 'Gilipollas detectado'
        }
        
        merror = {
            '403': '403 - Permiso denegado',
            '403c': '403 - Permiso denegado: debes repetir el captcha',
            '404': '404 - P&aacute;gina no encontrada en Ubuntu FAQ',
            '503': '503 - Error en Ubuntu FAQ,<br/>consulta el estado en: http://code.google.com/status/appengine',
            '606': '606 - Hemos detectado un gilipollas, TU!'
        }
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': str(cerror) + ' - Ubuntu FAQ',
            'descripcion': derror.get(cerror, 'Error desconocido'),
            'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': '404',
            'error': merror.get(cerror, 'Error desconocido'),
            'cerror': cerror,
            'captcha': chtml,
            'usuario': users.get_current_user(),
            'error_dominio': self.error_dominio
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/portada.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/', Portada),
                                        ('/inicio', Indice),
                                        ('/preguntas', Indice),
                                        (r'/preguntas/(.*)', Indice),
                                        ('/populares', Populares),
                                        ('/sin-solucionar', Sin_solucionar),
                                        ('/actualidad', Actualidad),
                                        (r'/actualidad/(.*)', Actualidad),
                                        ('/add_e', Actualidad),
                                        ('/images', Imagenes),
                                        (r'/images/(.*)', Imagenes),
                                        (r'/p/(.*)', Redir_pregunta),
                                        (r'/question/(.*)', Detalle_pregunta),
                                        ('/mod_p', Detalle_pregunta),
                                        ('/del_p', Borrar_pregunta),
                                        ('/stop_emails/(.*)', Stop_emails),
                                        ('/add_r', Responder),
                                        ('/dest_r', Destacar_respuesta),
                                        ('/mod_r', Modificar_respuesta),
                                        ('/del_r', Borrar_respuesta),
                                        (r'/e/(.*)', Acceder_enlace),
                                        (r'/de/(.*)', Redir_enlace),
                                        (r'/story/(.*)', Detalle_enlace),
                                        ('/mod_e', Detalle_enlace),
                                        ('/hun_e', Hundir_enlace),
                                        ('/del_e', Borrar_enlace),
                                        ('/add_c', Comentar),
                                        ('/mod_c', Modificar_comentario),
                                        ('/del_c', Borrar_comentario),
                                        (r'/u/(.*)', Detalle_usuario),
                                        ('/ayuda', Ayuda),
                                        ('/add_p', Nueva_pregunta),
                                        (r'/error/(.*)', Perror),
                                        ('/.*', Perror),
                                    ],
                                    debug=DEBUG_FLAG)
    webapp.template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

