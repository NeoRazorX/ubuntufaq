#!/usr/bin/env python

DEBUG_FLAG = True
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
WORDPRESS_PRIVATE_EMAIL = ''
STEAM_ENLACE_KEY = ''
RSS_LIST = ['http://diegocg.blogspot.com/feeds/posts/default',
    'http://neorazorx.blogspot.com/feeds/posts/default',
    'http://ubuntulife.wordpress.com/feed/',
    'http://www.linuxjuegos.com/wp-rss2.php',
    'http://feeds.feedburner.com/fayerwayer',
    'http://www.muylinux.com/feed/',
    'http://www.genbeta.com/index.xml']
KEYWORD_LIST = ['ubuntu', 'linux', 'canonical', 'unity', 'gnome', 'kde', 'x.org', 'android',
    'wayland', 'compiz', 'wine', 'ppa', 'lucid', 'maverick', 'natty', 'unix',
    'chrome os', 'kms', 'systemd', 'kernel', 'fedora', 'suse', 'debian', 'gcc',
    'gnu', 'linus', 'gallium3d', 'nouveau', 'opengl', 'xfs', 'ext3', 'ext4', 'btrfs']

import math
from google.appengine.ext import db, webapp
from google.appengine.api import users

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

class Comentario(db.Model):
    autor = db.UserProperty()
    id_enlace = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    puntos = db.IntegerProperty(default=0)
    os = db.StringProperty(default="desconocido")

# clase base
class Pagina(webapp.RequestHandler):
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

