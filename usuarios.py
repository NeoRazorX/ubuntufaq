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

import os, logging, cgi, urllib

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from base import *

class Detalle_usuario(Pagina):
    def get_preguntas(self, usuario, num=10):
        preguntas = memcache.get('preguntas_de_' + usuario.nickname())
        if preguntas is None:
            preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1 ORDER BY creado DESC", usuario).fetch(num)
            memcache.add('preguntas_de_' + usuario.nickname(), preguntas, 3600)
        else:
            logging.info('Leyendo ultimas-preguntas de memcache')
        return preguntas
    
    def get_respuestas(self, usuario, num=10):
        respuestas = memcache.get('respuestas_de_' + usuario.nickname())
        if respuestas is None:
            respuestas = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(num)
            memcache.add('respuestas_de_' + usuario.nickname(), respuestas, 3600)
        else:
            logging.info('Leyendo ultimas-respuestas de memcache')
        return respuestas
    
    def get_enlaces(self, usuario, num=10):
        enlaces = memcache.get('enlaces_de_' + usuario.nickname())
        if enlaces is None:
            enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1 ORDER BY creado DESC", usuario).fetch(num)
            memcache.add('enlaces_de_' + usuario.nickname(), enlaces, 3600)
        else:
            logging.info('Leyendo ultimos-enlaces de memcache')
        return enlaces
    
    def get_comentarios(self, usuario, num=10):
        comentarios = memcache.get('comentarios_de_' + usuario.nickname())
        if comentarios is None:
            comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1 ORDER BY fecha DESC", usuario).fetch(num)
            memcache.add('comentarios_de_' + usuario.nickname(), comentarios, 3600)
        else:
            logging.info('Leyendo ultimos-comentarios de memcache')
        return comentarios
    
    def get(self, email=None):
        Pagina.get(self)
        continuar = False
        if email:
            try:
                tusuario = users.User( urllib.unquote( email ) )
                if tusuario == users.get_current_user():
                    n = self.get_notificaciones()
                else:
                    n = []
                p = self.get_preguntas(tusuario, 20)
                r = self.get_respuestas(tusuario, 10)
                e = self.get_enlaces(tusuario, 10)
                c = self.get_comentarios(tusuario, 10)
                continuar = True
            except:
                pass
        if continuar:
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
                    'titulo': 'Perfil de ' + tusuario.nickname(),
                    'descripcion': 'Resumen del historial del usuario ' + tusuario.nickname() + ' en Ubuntu FAQ',
                    'tags': 'ubuntu, kubuntu, xubuntu, lubuntu, problema, ayuda, linux, karmic, lucid, maverick, natty, ocelot, ' + tusuario.nickname(),
                    'notificaciones': n,
                    'preguntas': p,
                    'respuestas': r,
                    'enlaces': e,
                    'comentarios': c,
                    'tusuario': tusuario,
                    'karma': karma,
                    'url': self.url,
                    'url_linktext': self.url_linktext,
                    'mi_perfil': self.mi_perfil,
                    'usuario': users.get_current_user(),
                    'notis': self.get_notificaciones(),
                    'formulario' : self.formulario,
                    'error_dominio': self.error_dominio
            }
            path = os.path.join(os.path.dirname(__file__), 'templates/usuario.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')

def main():
    application = webapp.WSGIApplication( [(r'/u/(.*)', Detalle_usuario)], debug=DEBUG_FLAG )
    template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
