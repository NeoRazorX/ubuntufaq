#!/usr/bin/env python

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

class Respuesta(db.Model):
    autor = db.UserProperty()
    id_pregunta = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    destacada = db.BooleanProperty(default=False)
    puntos = db.IntegerProperty(default=0)

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

class Comentario(db.Model):
    autor = db.UserProperty()
    id_enlace = db.StringProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    puntos = db.IntegerProperty(default=0)

# clase base
class Pagina(webapp.RequestHandler):
    def get(self):
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

