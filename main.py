#!/usr/bin/env python

import cgi, os, urllib
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from base import *
from pregunta import *
from actualidad import *
from imagenes import *

# clase para listar las preguntas
class Indice(Pagina):
    def get(self, p=0, vista='inicio'):
        Pagina.get(self)
        
        # filtramos
        if vista == 'sin-solucionar':
            p_query = db.GqlQuery("SELECT * FROM Pregunta WHERE estado < 10 ORDER BY estado ASC")
            enlaces = None
            respuestas = Respuesta.all().order('-fecha').fetch(15)
        elif vista == 'populares':
            p_query = db.GqlQuery("SELECT * FROM Pregunta ORDER BY visitas DESC")
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY clicks DESC").fetch(15)
            respuestas = None
        else:
            p_query = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC")
            enlaces = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(15)
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
                p = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(10)
                r = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(10)
                e = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(10)
                c = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(10)
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
                karma = p[0].puntos
            elif r:
                karma = r[0].puntos
            elif e:
                karma = e[0].puntos
            elif c:
                karma = c[0].puntos
            
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
    application = webapp.WSGIApplication([('/', Indice),
                                        ('/inicio', Indice),
                                        ('/populares', Populares),
                                        ('/sin-solucionar', Sin_contestar),
                                        ('/actualidad', Actualidad),
                                        ('/images', Imagenes),
                                        (r'/inicio/(.*)', Indice),
                                        (r'/populares/(.*)', Populares),
                                        (r'/sin-solucionar/(.*)', Sin_contestar),
                                        (r'/actualidad/(.*)', Actualidad),
                                        (r'/images/(.*)', Imagenes),
                                        (r'/p/(.*)', Redir_pregunta),
                                        (r'/question/(.*)', Detalle_pregunta),
                                        (r'/e/(.*)', Acceder_enlace),
                                        (r'/de/(.*)', Redir_enlace),
                                        (r'/story/(.*)', Detalle_enlace),
                                        (r'/u/(.*)', Detalle_usuario),
                                        ('/ayuda', Ayuda),
                                        ('/buscar', Buscar),
                                        ('/nueva', Nueva_pregunta),
                                        ('/add_p', Preguntar),
                                        ('/add_r', Responder),
                                        ('/add_e', Enlazar),
                                        ('/add_c', Comentar),
                                        ('/dest_r', Destacar_respuesta),
                                        ('/mod_p', Modificar_pregunta),
                                        ('/mod_r', Modificar_respuesta),
                                        ('/mod_e', Modificar_enlace),
                                        ('/mod_c', Modificar_comentario),
                                        ('/del_r', Borrar_respuesta),
                                        ('/del_p', Borrar_pregunta),
                                        ('/del_e', Borrar_enlace),
                                        ('/del_c', Borrar_comentario),
                                        (r'/error/(.*)', Perror),
                                        ('/.*', Perror),
                                    ],
                                    debug=True)
    webapp.template.register_template_library('filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

