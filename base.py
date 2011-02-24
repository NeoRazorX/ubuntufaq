#!/usr/bin/env python

DEBUG_FLAG = True
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
WORDPRESS_PRIVATE_EMAIL = ''
STEAM_ENLACE_KEY = ''
RSS_LIST = ['http://diegocg.blogspot.com/feeds/posts/default',
    'http://neorazorx.blogspot.com/feeds/posts/default',
    'http://ubuntulife.wordpress.com/feed/',
    'http://feeds.feedburner.com/fayerwayer',
    'http://www.muylinux.com/feed/',
    'http://www.genbeta.com/index.xml']
KEYWORD_LIST = ['ubuntu', 'linux', 'canonical', 'unity', 'gnome', 'kde', 'x.org', 'android',
    'wayland', 'compiz', 'wine', 'ppa', 'lucid', 'maverick', 'natty', 'unix', 'plymouth',
    'chrome os', 'kms', 'systemd', 'kernel', 'fedora', 'suse', 'debian', 'gcc', 'grub',
    'gnu', 'linus', 'gallium3d', 'nouveau', 'opengl', 'xfs', 'ext3', 'ext4', 'btrfs']
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
    estado = db.IntegerProperty(default=0)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")
    
    # actualizamos las visitas, no pasa nada si no se puede
    def visitar(self, ip):
        if self.ultima_ip != ip:
            self.ultima_ip = ip
            self.visitas += 1
            try:
                self.put()
            except:
                pass
    
    # devuelve las respuesta a esta pregunta
    def get_respuestas(self, numero=100):
        respuestas = memcache.get( str(self.key()) )
        if respuestas is not None:
            logging.info('Leyendo de memcache para: ' + str(self.key()) )
        else:
            respuestas = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1 ORDER BY fecha ASC", str(self.key())).fetch(numero)
            if not memcache.add( str(self.key()), respuestas ):
                logging.error("Fallo almacenando en memcache: " + str(self.key()) )
            else:
                logging.info('Almacenando en memcache: ' + str(self.key()) )
        return respuestas
    
    # actualizamos la fecha y el numero de respuestas
    def actualizar(self):
        self.respuestas = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1", str(self.key())).count()
        self.fecha = datetime.now()
        self.put()
    
    # borramos la cache que contenga esta pregunta
    def borrar_cache(self):
        memcache.delete( str(self.key()) )
        memcache.delete( 'portada' )

class Respuesta(db.Model):
    autor = db.UserProperty()
    id_pregunta = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    destacada = db.BooleanProperty(default=False)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")

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
    
    # actualizamos los clicks, no pasa nada si no podemos
    def clickar(self, ip):
        if self.ultima_ip != ip:
            self.ultima_ip = ip
            self.clicks += 1
            try:
                self.put()
            except:
                pass
    
    # devuelve los comentarios del enlace
    def get_comentarios(self, numero=100):
        comentarios = memcache.get( str(self.key()) )
        if comentarios is not None:
            logging.info('Leyendo de memcache para: ' + str(self.key()))
        else:
            comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", str(self.key())).fetch(numero)
            if not memcache.add( str(self.key()), comentarios):
                logging.error("Fallo almacenando en memcache: " + str(self.key()) )
            else:
                logging.info('Almacenando en memcache: ' + str(self.key()) )
        return comentarios
    
    # actualizamos la fecha y numero de comentarios del enlace
    def actualizar(self):
        self.comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1", str(self.key())).count()
        self.fecha = datetime.now()
        self.put()
    
    # borramos la cache que contenga este enlace
    def borrar_cache(self):
        memcache.delete( str(self.key()) )
        memcache.delete( 'portada' )

class Comentario(db.Model):
    autor = db.UserProperty()
    id_enlace = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")

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
        if self.request.uri[7:29] == 'ubuntu-faq.appspot.com':
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
            self.url_linktext = 'entra con tu cuenta Google'
            self.formulario = False
            self.mi_perfil = '/'
    
    def paginar(self, query, limite, actual):
        # calculamos todo lo necesario para paginar
        paginas = int( math.ceil( query.count() / float(limite) ) )
        if paginas < 1:
            paginas = 1
        elif paginas > 10:
            paginas = 10
        
        try:
            p_actual = int(actual)
        except:
            p_actual = 0
        
        # paginamos
        return query.fetch(limite, int(limite * p_actual) ), paginas, p_actual

