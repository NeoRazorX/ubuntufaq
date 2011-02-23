#!/usr/bin/env python

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
            elif preguntas[p].fecha > enlaces[e].fecha:
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
        mixto = memcache.get( 'portada' )
        if mixto is not None:
            logging.info('Leyendo de memcache para la portada')
        else:
            mixto = self.mezclar()
            if not memcache.add('portada', mixto):
                logging.error("Fallo almacenando en memcache la portada ")
            else:
                logging.info('Almacenando en memcache la portada')
        return mixto
    
    def get(self):
        Pagina.get(self)
        mixto = self.get_portada()
        vista = 'portada'
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': 'Ubuntu FAQ - ' + vista,
            'descripcion': vista + ' - Soluciones rapidas para tus problemas con Ubuntu linux, asi como dudas y noticias. Si tienes alguna duda compartela con nosotros!',
            'tags': 'ubufaq, ubuntu faq, problema ubuntu, linux, karmin, lucid, maverick, natty',
            'mixto': mixto,
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'captcha': chtml,
            'usuario': users.get_current_user(),
            'vista': vista,
            'error_dominio': self.error_dominio
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/portada.html')
        self.response.out.write( template.render(path, template_values) )

# clase para listar las preguntas
class Indice(Pagina):
    def get(self, p=0, vista='inicio'):
        Pagina.get(self)
        
        # filtramos
        if vista == 'sin-solucionar':
            p_query = db.GqlQuery("SELECT * FROM Pregunta WHERE estado < 10 ORDER BY estado ASC")
            enlaces = None
            respuestas = db.GqlQuery("SELECT * FROM Respuesta ORDER BY fecha DESC LIMIT 18")
        elif vista == 'populares':
            p_query = db.GqlQuery("SELECT * FROM Pregunta ORDER BY visitas DESC")
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY clicks DESC LIMIT 18")
            respuestas = None
        else:
            p_query = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC")
            enlaces = None
            respuestas = None
            vista = 'inicio'
        
        # paginamos
        preguntas, paginas, p_actual = self.paginar(p_query, 20, p)
        
        template_values = {
            'titulo': 'Ubuntu FAQ - ' + vista,
            'descripcion': vista + ' - Soluciones rapidas para tus problemas con Ubuntu linux, asi como dudas y noticias. Si tienes alguna duda compartela con nosotros!',
            'tags': 'ubufaq, ubuntu faq, problema ubuntu, linux, karmin, lucid, maverick, natty',
            'preguntas': preguntas,
            'respuestas': respuestas,
            'enlaces': enlaces,
            'paginas': paginas,
            'rango_paginas': range(paginas),
            'pag_actual': p_actual,
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario' : self.formulario,
            'vista': vista,
            'error_dominio': self.error_dominio
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write( template.render(path, template_values) )

class Populares(Indice):
    def get(self, p=0):
        Indice.get(self, p, 'populares')

class Sin_contestar(Indice):
    def get(self, p=0):
        Indice.get(self, p, 'sin-solucionar')

class Ayuda(Pagina):
    def get(self):
        Pagina.get(self)
        
        template_values = {
            'titulo': 'Ayuda de Ubuntu FAQ',
            'descripcion': 'Seccion de ayuda de Ubuntu FAQ. Soluciones rapidas para tus problemas con Ubuntu',
            'tags': 'ubufaq, ubuntu FAQ, problema ubuntu, ayuda ubuntu, linux, lucid, maverick, natty',
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
        
        if email:
            try:
                usuario = users.User( urllib.unquote( email ) )
                p = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1 ORDER BY fecha DESC LIMIT 10", usuario)
                r = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1 ORDER BY fecha DESC LIMIT 10", usuario)
                e = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1 ORDER BY fecha DESC LIMIT 10", usuario)
                c = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1 ORDER BY fecha DESC LIMIT 10", usuario)
                continuar = True
            except:
                pass
        
        if continuar:
            if usuario == users.get_current_user():
                vista = 'mi-perfil'
            else:
                vista = ''
            
            karma = 0
            if r:
                for col in r:
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
                'tags': 'ubufaq, ubuntu FAQ, problema ubuntu, linux, lucid, maverick, natty, ' + str(usuario),
                'paginas': 1,
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

class Buscar(Pagina):
    def get(self):
        Pagina.get(self)
        
        template_values = {
            'titulo': 'Buscador de Ubuntu FAQ',
            'descripcion': 'Buscador de Ubuntu FAQ, soluciones rapidas para tus problemas con Ubuntu',
            'tags': 'ubufaq, ubuntu FAQ, problema ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'buscar',
            'error_dominio': self.error_dominio
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/buscar.html')
        self.response.out.write(template.render(path, template_values))

class Perror(Pagina):
    def get(self, cerror='404'):
        Pagina.get(self)
        
        derror = {
            '403': 'Permiso denegado',
            '403c': 'Permiso denegado - error en el captcha',
            '404': 'Pagina no encontrada en Ubuntu FAQ',
            '503': 'Error en Ubuntu FAQ',
        }
        
        merror = {
            '403': '403 - Permiso denegado',
            '403c': '403 - Permiso denegado: debes repetir el captcha',
            '404': '404 - P&aacute;gina no encontrada en Ubuntu FAQ',
            '503': '503 - Error en Ubuntu FAQ,<br/>consulta el estado en: http://code.google.com/status/appengine',
        }
        
        template_values = {
            'titulo': str(cerror) + ' - Ubuntu FAQ',
            'descripcion': derror.get(cerror, 'Error desconocido'),
            'tags': 'ubufaq, ubuntu FAQ, problema ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': '404',
            'error': merror.get(cerror, 'Error desconocido'),
            'cerror': cerror,
            'error_dominio': self.error_dominio
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/buscar.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/', Portada),
                                        ('/inicio', Indice),
                                        (r'/inicio/(.*)', Indice),
                                        ('/populares', Populares),
                                        (r'/populares/(.*)', Populares),
                                        ('/sin-solucionar', Sin_contestar),
                                        (r'/sin-solucionar/(.*)', Sin_contestar),
                                        ('/actualidad', Actualidad),
                                        (r'/actualidad/(.*)', Actualidad),
                                        ('/add_e', Actualidad),
                                        ('/images', Imagenes),
                                        (r'/images/(.*)', Imagenes),
                                        (r'/p/(.*)', Redir_pregunta),
                                        (r'/question/(.*)', Detalle_pregunta),
                                        ('/mod_p', Detalle_pregunta),
                                        ('/del_p', Borrar_pregunta),
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
                                        ('/buscar', Buscar),
                                        ('/nueva', Nueva_pregunta),
                                        ('/add_p', Nueva_pregunta),
                                        (r'/error/(.*)', Perror),
                                        ('/.*', Perror),
                                    ],
                                    debug=DEBUG_FLAG)
    webapp.template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

