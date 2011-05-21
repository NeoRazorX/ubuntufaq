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

DEBUG_FLAG = True
APP_NAME = 'ubuntu-faq'
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
WORDPRESS_PRIVATE_EMAIL = ''
STEAM_ENLACE_KEY = ''
RSS_LIST = ['http://diegocg.blogspot.com/feeds/posts/default',
    'http://neorazorx.blogspot.com/feeds/posts/default']
KEYWORD_LIST = ['ubuntu', 'kubuntu', 'xubuntu', 'lubuntu', 'linux', 'android', 'meego', 'fedora', 'gentoo',
    'suse', 'debian', 'unix', 'canonical', 'lucid', 'maverick', 'natty', 'ocelot', 'chrome os',
    'unity', 'gnome', 'kde', 'xfce', 'enlightment', 'x.org', 'wayland', 'compiz', 'alsa',
    'plymouth', 'kms', 'systemd', 'kernel', 'gcc', 'grub', 'wine', 'ppa', 'gallium3d',
    'nouveau', 'opengl', 'xfs', 'ext3', 'ext4', 'btrfs',
    'gnu', 'linus', 'desura', 'libreoffice', 'nautilus']
SITEMAP_CACHE_TIME = 14400

import math, logging
from google.appengine.ext import db, webapp
from google.appengine.api import users, memcache
from datetime import datetime

class Pregunta(db.Model):
    autor = db.UserProperty()
    titulo = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    creado = db.DateTimeProperty(auto_now_add=True)
    respuestas = db.IntegerProperty(default=0)
    tags = db.StringProperty()
    visitas = db.IntegerProperty(default=0)
    ultima_ip = db.StringProperty(default="0.0.0.0")
    enviar_email = db.BooleanProperty(default=False)
    stop_emails = db.BooleanProperty(default=True)
    estado = db.IntegerProperty(default=0)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")
    
    # devuelve las respuesta a esta pregunta
    # ademas suma una visita si se le proporciona una ip
    def get_respuestas(self, ip = None):
        respuestas = memcache.get( str(self.key()) )
        if respuestas is None:
            query = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1 ORDER BY fecha ASC", str(self.key()))
            respuestas = query.fetch( query.count() )
            if memcache.add( str(self.key()), respuestas ):
                logging.info('Almacenando en memcache: ' + str(self.key()) )
            else:
                logging.warning("Fallo almacenando en memcache: " + str(self.key()) )
        else:
            logging.info('Leyendo de memcache para: ' + str(self.key()) )
        cambio = False
        if self.respuestas != len( respuestas ):
            self.respuestas = len( respuestas )
            cambio = True
        if ip and self.ultima_ip != ip:
            self.ultima_ip = ip
            self.visitas += 1
            cambio = True
        if cambio:
            try:
                self.put()
                self.borrar_cache()
            except:
                logging.warning("Fallo actualizando la pregunta: " + str(self.key()) )
        return respuestas
    
    def get_link(self):
        return '/question/' + str(self.key())
    
    # actualizamos varios datos de la pregunta
    def actualizar(self, respuesta=None):
        self.fecha = datetime.now()
        
        if respuesta:
            # cambiamos el estado de la pregunta en funcion de la respuesta
            if respuesta.autor:
                if respuesta.autor == self.autor:
                    if respuesta.contenido.lower().find('solucionad') != -1:
                        self.estado = 10
                elif self.estado == 0:
                    self.estado = 2
            elif self.estado == 0:
                self.estado = 2
            # volvemos a marcar la pregunta para enviar un email hasta que se solucione o stop_emails == True
            if self.autor and not self.stop_emails and self.estado < 10:
                self.enviar_email = True
        
        # guardamos los cambios
        self.put()
        self.borrar_cache()
    
    def borrar_respuestas(self):
        r = Respuesta.all().filter('id_pregunta =', self.key())
        db.delete(r)
    
    # borramos la cache que contenga esta pregunta
    def borrar_cache(self):
        memcache.delete_multi([str(self.key()), 'portada', 'sin-solucionar', 'populares', 'sitemap_preguntas'])
    
    def borrar_todo(self):
        self.borrar_respuestas()
        self.borrar_cache()
        self.delete()

class Respuesta(db.Model):
    autor = db.UserProperty()
    id_pregunta = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    destacada = db.BooleanProperty(default=False)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")
    
    def get_pregunta(self):
        try:
            return Pregunta.get( self.id_pregunta )
        except:
            return None
    
    def destacar(self):
        self.destacada = not(self.destacada)
        self.put()
        memcache.delete( self.id_pregunta )

class Enlace(db.Model):
    autor = db.UserProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    creado = db.DateTimeProperty(auto_now_add=True)
    descripcion = db.StringProperty()
    url = db.LinkProperty()
    tipo_enlace = db.StringProperty()
    clicks = db.IntegerProperty(default=0)
    ultima_ip = db.StringProperty(default="0.0.0.0")
    comentarios = db.IntegerProperty(default=0)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")
    
    # devuelve los comentarios del enlace
    # ademas suma un clic si se le proporciona una ip
    def get_comentarios(self, ip=None):
        comentarios = memcache.get( str(self.key()) )
        if comentarios is None:
            query = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", str(self.key()))
            comentarios = query.fetch( query.count() )
            if memcache.add( str(self.key()), comentarios):
                logging.info('Almacenando en memcache: ' + str(self.key()) )
            else:
                logging.warning("Fallo almacenando en memcache: " + str(self.key()) )
        else:
            logging.info('Leyendo de memcache para: ' + str(self.key()))
        cambio = False
        if self.comentarios != len( comentarios ):
            self.comentarios = len( comentarios )
            cambio = True
        if ip and self.ultima_ip != ip:
            self.ultima_ip = ip
            self.clicks += 1
            cambio = True
        if cambio:
            try:
                self.put()
                self.borrar_cache()
            except:
                logging.warning("Fallo actualizando el enlace: " + str(self.key()) )
        return comentarios
    
    def get_link(self):
        return '/story/' + str(self.key())
    
    def hundir(self):
        self.fecha = datetime.min
        self.put()
        self.borrar_cache()
        logging.warning('Se ha hundido el enlace con id: ' + str(self.key()))
    
    # actualizamos la fecha y numero de comentarios del enlace
    def actualizar(self):
        self.fecha = datetime.now()
        self.put()
    
    def borrar_comentarios(self):
        c = Comentario.all().filter('id_enlace =', self.key())
        db.delete(c)
    
    # borramos la cache que contenga este enlace
    def borrar_cache(self):
        memcache.delete_multi([str(self.key()), 'portada', 'populares', 'sitemap_enlaces'])
    
    def borrar_todo(self):
        self.borrar_comentarios()
        self.borrar_cache()
        self.delete()

class Comentario(db.Model):
    autor = db.UserProperty()
    id_enlace = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")
    
    def get_enlace(self):
        try:
            return Enlace.get( self.id_enlace )
        except:
            return None

# clase base
class Pagina(webapp.RequestHandler):
    def extraer_tags(self, texto):
        retorno = ''
        for tag in KEYWORD_LIST:
            if texto.lower().find(tag) != -1:
                if retorno == '':
                    retorno = tag
                else:
                    retorno += ', ' + tag
        if retorno == '':
            retorno = 'ubuntu, general'
        return retorno
    
    def get(self):
        # comprobamo que no hayan accedido a la web por appspot
        if self.request.uri[7:29] == APP_NAME + '.appspot.com':
            self.error_dominio = True
        else:
            self.error_dominio = False
        
        if users.get_current_user():
            self.url = users.create_logout_url( self.request.uri )
            self.url_linktext = 'salir'
            self.formulario = True
            self.mi_perfil = '/u/' + users.get_current_user().email()
        else:
            self.url = users.create_login_url( self.request.uri )
            self.url_linktext = 'login'
            self.formulario = False
            self.mi_perfil = '/'
    
    def paginar(self, query, limite=20, actual=0):
        # calculamos todo lo necesario para paginar
        paginas = int( math.ceil( query.count() / float(limite) ) )
        if paginas < 1:
            paginas = 1
        
        try:
            p_actual = int(actual)
        except:
            p_actual = 0
        
        # paginamos
        return query.fetch(limite, int(limite * p_actual) ), paginas, p_actual

