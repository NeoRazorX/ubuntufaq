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

DEBUG_FLAG = True
APP_NAME = 'ubuntu-faq'
APP_DESCRIPTION = u'Soluciones rápidas para tus problemas con Ubuntu, Kubuntu, Xubuntu, Lubuntu, y linux en general, así como noticias, vídeos, wallpapers y enlaces de interés.'
APP_DOMAIN = ''
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
STEAM_ENLACE_KEY = ''
RSS_LIST = ['http://diegocg.blogspot.com/feeds/posts/default',
    'http://www.cristianvicente.com/feed/',
    'http://neorazorx.blogspot.com/feeds/posts/default']
KEYWORD_LIST = ['ubuntu', 'kubuntu', 'xubuntu', 'lubuntu', 'linux', 'android', 'meego', 'fedora', 'gentoo',
    'suse', 'debian', 'unix', 'canonical', 'lucid', 'maverick', 'natty', 'ocelot', 'chrome os',
    'unity', 'gnome', 'kde', 'xfce', 'enlightment', 'x.org', 'wayland', 'compiz', 'alsa', 'gtk', 'gdk', 'qt',
    'plymouth', 'kms', 'systemd', 'kernel', 'gcc', 'grub', 'wine', 'ppa', 'gallium3d', 'gdm',
    'nouveau', 'opengl', 'xfs', 'ext2', 'ext3', 'ext4', 'btrfs', 'reiser', 'mysql', 'postgresql',
    'gnu', 'linus', 'desura', 'libreoffice', 'nautilus', 'python', 'juego', 'wifi', '3g', 'bios', 'driver']

import math, random, logging, urllib, base64, re
from google.appengine.ext import db, webapp
from google.appengine.api import users, memcache
from datetime import datetime


class Pregunta(db.Model):
    autor = db.UserProperty()
    contenido = db.TextProperty()
    creado = db.DateTimeProperty(auto_now_add=True)
    estado = db.IntegerProperty(default=0)
    fecha = db.DateTimeProperty(auto_now_add=True)
    os = db.StringProperty(default='desconocido')
    puntos = db.IntegerProperty(default=0)
    respuestas = db.IntegerProperty(default=0)
    seguimientos = db.IntegerProperty(default=0)
    tags = db.StringProperty(default='')
    titulo = db.StringProperty(default='')
    ultima_ip = db.StringProperty(default='0.0.0.0')
    visitas = db.IntegerProperty(default=0)
    
    # devuelve las respuesta a esta pregunta
    # ademas suma una visita si se le proporciona una ip
    def get_respuestas(self, ip = None):
        respuestas = memcache.get( str(self.key()) )
        if respuestas is None:
            query = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1 ORDER BY fecha ASC", str(self.key()))
            respuestas = query.fetch( query.count() )
            if not memcache.add( str(self.key()), respuestas ):
                logging.warning('Imposible almacenar en memcache las respuestas de: ' + str(self.key()) )
        else:
            logging.info('Leyendo de memcache las respuestas para: ' + str(self.key()) )
        cambio = False
        if self.respuestas != len( respuestas ):
            if len( respuestas ) > self.respuestas:
                det = Detector_respuestas()
                det.detectar(respuestas, self.get_link())
            self.respuestas = len( respuestas )
            memcache.delete( str(self.key()) )
            cambio = True
        if ip and self.ultima_ip != ip:
            self.ultima_ip = ip
            self.visitas += 1
            cambio = True
        if cambio:
            try:
                self.put()
            except:
                logging.warning('Imposible actualizar la pregunta: ' + str(self.key()) )
        return respuestas
    
    # devuelve los datos de seguimiento de esta pregunta
    def get_seguimiento(self):
        seguimiento = memcache.get('seguimiento_' + str(self.key()))
        if seguimiento is None:
            query = db.GqlQuery("SELECT * FROM Seguimiento WHERE id_pregunta = :1", str(self.key()))
            seguimiento = query.fetch( query.count() )
            if not memcache.add('seguimiento_' + str(self.key()), seguimiento):
                logging.warning('Imposible almacenar en memcache el seguimiento de: ' + str(self.key()) )
        else:
            logging.info('Leyendo de memcache el seguimiento de: ' + str(self.key()) )
        cambio = False
        if not seguimiento:
            if self.seguimientos != 0:
                self.seguimientos = 0
                cambio = True
        elif self.seguimientos != len( seguimiento[0].usuarios ):
            self.seguimientos = len( seguimiento[0].usuarios )
            memcache.delete('seguimiento_' + str(self.key()))
            cambio = True
        if cambio:
            try:
                self.put()
            except:
                logging.warning('Imposible actualizar la pregunta: ' + str(self.key()) )
        if len( seguimiento ) == 0:
            return None
        else:
            return seguimiento[0]
    
    def get_tags(self):
        all_tags = memcache.get('all-tags')
        if all_tags is None:
            all_tags = []
            for tag in KEYWORD_LIST:
                all_tags.append([tag.lower(), 0])
        for tag in all_tags:
            if re.search('\\b'+tag[0]+'\\b', self.titulo.lower()+self.contenido.lower()):
                if tag[0].strip() != '' and self.tags.lower().find(tag[0]) == -1:
                    if self.tags == '':
                        self.tags = tag[0]
                    else:
                        self.tags += ', ' + tag[0]
        if self.tags == '':
            self.tags = 'general'
    
    def es_seguidor(self, usuario):
        s = self.get_seguimiento()
        if not usuario:
            return False
        elif usuario == self.autor:
            return True
        elif not s:
            return False
        elif usuario in s.usuarios:
            return True
        else:
            return False
    
    def get_link(self):
        return '/question/' + str(self.key())
    
    def get_full_link(self):
        return APP_DOMAIN + '/question/' + str(self.key())
    
    def get_estado(self):
        retorno = 'estado desconocido'
        if self.estado == 0:
            retorno = 'nueva'
        elif self.estado == 1:
            retorno = 'incompleta'
        elif self.estado == 2:
            retorno = 'abierta'
        elif self.estado == 3:
            retorno = 'parcialmente solucionada'
        elif self.estado == 10:
            retorno = 'solucionada'
        elif self.estado == 11:
            retorno = u'pendiente de confirmación'
        elif self.estado == 12:
            retorno = 'duplicada'
        elif self.estado == 13:
            retorno = 'erronea'
        elif self.estado == 14:
            retorno = 'antigua'
        return retorno
    
    # actualizamos varios datos de la pregunta
    def actualizar(self, respuesta=None):
        self.fecha = datetime.now()
        if respuesta:
            # cambiamos el estado de la pregunta en funcion de la respuesta
            if respuesta.autor and respuesta.autor == self.autor and respuesta.contenido.lower().find('solucionad') != -1:
                self.estado = 10
                self.marcar_solucionada()
            elif self.estado == 0:
                self.estado = 2
            # añadimos una notificación
            if self.autor and self.autor != respuesta.autor:
                try:
                    n = Notificacion()
                    n.usuario = self.autor
                    n.link = self.get_link()
                    if respuesta.autor:
                        n.mensaje = 'El usuario ' + respuesta.autor.nickname() + ' ha contestado a tu pregunta "' + self.titulo[:99] + '".'
                    else:
                        n.mensaje = u'Un anónimo ha contestado a tu pregunta "' + self.titulo[:99] + '".'
                    n.put()
                    n.borrar_cache()
                except:
                    logging.error('Imposible guardar la notificación')
        # guardamos los cambios
        self.put()
        self.borrar_cache()
    
    def marcar_pendiente(self):
        if self.autor:
            # añadimos una notificación
            try:
                n = Notificacion()
                n.usuario = self.autor
                n.link = self.get_link()
                n.mensaje = u'Un administrador te solicita que confirmes la solución a tu pregunta "' + self.titulo[:99] + '".'
                n.put()
                n.borrar_cache()
            except:
                logging.error('Imposible guardar la notificación')
    
    def marcar_solucionada(self):
        if self.autor:
            # añadimos una notificación
            try:
                n = Notificacion()
                n.usuario = self.autor
                n.link = self.get_link()
                n.mensaje = 'Tu pregunta "' + self.titulo[:99] + '" ha sido marcada como solucionada.'
                n.put()
                n.borrar_cache()
            except:
                logging.error('Imposible guardar la notificación')
    
    def borrar_respuestas(self):
        r = Respuesta.all().filter('id_pregunta =', self.key())
        db.delete(r)
    
    def borrar_seguimiento(self):
        s = db.GqlQuery("SELECT * FROM Seguimiento WHERE id_pregunta = :1", str(self.key()))
        db.delete(s)
    
    def borrar_busquedas(self):
        b = db.GqlQuery("SELECT * FROM Busqueda WHERE url = :1", self.get_link())
        db.delete(b)
    
    # borramos la cache que contenga esta pregunta
    def borrar_cache(self):
        memcache.delete_multi([str(self.key()), 'seguimiento_' + str(self.key()), 'portada',
                               'sin-solucionar', 'populares', 'sitemap_preguntas', 'ultimas-respuestas'])
    
    def borrar_todo(self):
        self.borrar_respuestas()
        self.borrar_seguimiento()
        self.borrar_busquedas()
        self.borrar_cache()
        self.delete()


class Respuesta(db.Model):
    autor = db.UserProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    id_pregunta = db.StringProperty()
    ips = db.StringListProperty()
    os = db.StringProperty(default='desconocido')
    puntos = db.IntegerProperty(default=0) # del autor
    valoracion = db.IntegerProperty(default=0)
    
    def get_pregunta(self):
        try:
            return Pregunta.get( self.id_pregunta )
        except:
            return None
    
    def borrar_cache(self):
        memcache.delete( self.id_pregunta )


class Enlace(db.Model):
    autor = db.UserProperty()
    clicks = db.IntegerProperty(default=0)
    comentarios = db.IntegerProperty(default=0)
    creado = db.DateTimeProperty(auto_now_add=True)
    descripcion = db.StringProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    os = db.StringProperty(default='desconocido')
    puntos = db.IntegerProperty(default=0)
    tags = db.StringProperty(default='')
    tipo_enlace = db.StringProperty()
    url = db.LinkProperty()
    ultima_ip = db.StringProperty(default='0.0.0.0')
    
    def comprobar(self):
        if self.url is None:
            self.url = APP_DOMAIN + self.get_link()
            self.put()
    
    # devuelve los comentarios del enlace
    # ademas suma un clic si se le proporciona una ip
    def get_comentarios(self, ip=None):
        comentarios = memcache.get( str(self.key()) )
        if comentarios is None:
            query = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", str(self.key()))
            comentarios = query.fetch( query.count() )
            if not memcache.add( str(self.key()), comentarios):
                logging.warning('Imposible almacenar en memcache: ' + str(self.key()) )
        else:
            logging.info('Leyendo de memcache para: ' + str(self.key()))
        cambio = False
        if self.comentarios != len( comentarios ):
            if len( comentarios ) > self.comentarios:
                # añadimos las notificaciones pertinentes
                if self.autor and len( comentarios ) == 1:
                    try:
                        n = Notificacion()
                        n.usuario = self.autor
                        n.link = self.get_link()
                        n.mensaje = 'Han comentado tu enlace ' + self.descripcion[:99] + '...'
                        n.put()
                        n.borrar_cache()
                    except:
                        logging.warning('Imposible guardar la notificación')
                else:
                    det = Detector_respuestas()
                    det.detectar(comentarios, self.get_link())
            self.comentarios = len( comentarios )
            memcache.delete( str(self.key()) )
            cambio = True
        if ip and self.ultima_ip != ip:
            self.ultima_ip = ip
            self.clicks += 1
            cambio = True
        if not self.tags:
            self.get_tags()
            cambio = True
        if cambio:
            try:
                self.put()
            except:
                logging.warning('Imposible actualizar el enlace: ' + str(self.key()) )
        return comentarios
    
    def get_link(self):
        return '/story/' + str(self.key())
    
    def get_full_link(self):
        return APP_DOMAIN + '/story/' + str(self.key())
    
    def get_tags(self):
        all_tags = memcache.get('all-tags')
        if all_tags is None:
            all_tags = []
            for tag in KEYWORD_LIST:
                all_tags.append([tag.lower(), 0])
        for tag in all_tags:
            if re.search('\\b'+tag[0]+'\\b', self.descripcion.lower()):
                if self.tags.lower().find(tag[0]) == -1 and tag[0].strip() != '':
                    if self.tags == '':
                        self.tags = tag[0]
                    else:
                        self.tags += ', ' + tag[0]
        if self.tags == '':
            self.tags = 'general'
    
    def hundir(self):
        self.fecha = datetime.min
        self.put()
        self.borrar_cache()
        logging.warning('Se ha hundido el enlace con id: ' + str(self.key()))
    
    # actualizamos la fecha del enlace
    def actualizar(self):
        self.fecha = datetime.now()
        self.put()
        self.borrar_cache()
    
    def borrar_comentarios(self):
        c = Comentario.all().filter('id_enlace =', self.key())
        db.delete(c)
    
    def borrar_busquedas(self):
        b = db.GqlQuery("SELECT * FROM Busqueda WHERE url = :1", self.get_link())
        db.delete(b)
    
    # borramos la cache que contenga este enlace
    def borrar_cache(self):
        memcache.delete_multi([str(self.key()), 'portada', 'populares', 'sitemap_enlaces'])
    
    def borrar_todo(self):
        self.borrar_comentarios()
        self.borrar_busquedas()
        self.borrar_cache()
        self.delete()


class Comentario(db.Model):
    autor = db.UserProperty()
    contenido = db.TextProperty()
    fecha = db.DateTimeProperty(auto_now_add=True)
    id_enlace = db.StringProperty()
    os = db.StringProperty(default="desconocido")
    puntos = db.IntegerProperty(default=0)
    
    def get_enlace(self):
        try:
            return Enlace.get( self.id_enlace )
        except:
            return None


class Notificacion(db.Model):
    email = db.BooleanProperty(default=True) # ¿Enviar email?
    fecha = db.DateTimeProperty(auto_now_add=True)
    link = db.StringProperty(default='/')
    mensaje = db.StringProperty(default=u'Notificación vacía.')
    usuario = db.UserProperty()
    
    def borrar_cache(self):
        memcache.delete('notificaciones_' + str(self.usuario))


class Detector_respuestas():
    def detectar(self, conjunto=[], link='/'):
        num = len(conjunto)
        if num > 1:
            i = num - 1
            while i >= 0:
                if conjunto[num-1].contenido.find('@' + str(i) + ' ') != -1 and conjunto[i-1].autor:
                    try:
                        n = Notificacion()
                        n.usuario = conjunto[i-1].autor
                        n.link = link + '#' + str(i)
                        if conjunto[num-1].autor:
                            n.mensaje = 'El usuario ' + conjunto[num-1].autor.nickname() + ' te ha contestado.'
                        else:
                            n.mensaje = u'Un anónimo te ha contestado.'
                        n.put()
                        n.borrar_cache()
                    except:
                        logging.error('Imposible guardar la notificación')
                i -= 1


class Busqueda(db.Model):
    tag = db.StringProperty()
    url = db.StringProperty()
    text = db.StringProperty()
    clics = db.IntegerProperty(default=0)


# clase para gestionar el siguimiento de preguntas
class Seguimiento(db.Model):
    estado = db.IntegerProperty(default=0)
    id_pregunta = db.StringProperty()
    respuestas = db.IntegerProperty(default=0)
    usuarios = db.ListProperty( users.User )
    
    def get_pregunta(self):
        try:
            return Pregunta.get( self.id_pregunta )
        except:
            return None
    
    def borrar_cache(self):
        memcache.delete('seguimiento_' + self.id_pregunta)


class Usuario(db.Model):
    comentarios = db.IntegerProperty(default=0)
    emails = db.BooleanProperty(default=True) # ¿Enviar emails?
    enlaces = db.IntegerProperty(default=0)
    iterador = db.IntegerProperty(default=0)
    fecha = db.DateTimeProperty(auto_now_add=True)
    preguntas = db.IntegerProperty(default=0)
    puntos = db.FloatProperty(default=0.0)
    respuestas = db.IntegerProperty(default=0)
    usuario = db.UserProperty()
    
    def get_link(self):
        return base64.b64decode( urllib.unquote( self.usuario.email() ) )


# clase base
class Pagina(webapp.RequestHandler):
    def extraer_tags(self, texto):
        retorno = ''
        all_tags = memcache.get('all-tags')
        if all_tags is None:
            all_tags = []
            for tag in KEYWORD_LIST:
                all_tags.append([tag.lower(), 0])
        for tag in all_tags:
            if re.search('\\b'+tag[0].lower()+'\\b', texto.lower()):
                if tag[0].strip() != '':
                    if retorno == '':
                        retorno = tag[0]
                    else:
                        retorno += ', ' + tag[0]
        if retorno == '':
            retorno = 'general'
        return retorno
    
    def get(self):
        # comprobamo que no hayan accedido a la web por appspot
        if self.request.uri[:21] != APP_DOMAIN and self.request.uri[:16] != 'http://localhost':
            self.error_dominio = True
        else:
            self.error_dominio = False
        
        if users.get_current_user():
            self.url = users.create_logout_url( self.request.uri )
            self.url_linktext = 'salir'
            self.formulario = True
            self.mi_perfil = '/u/' + urllib.quote( base64.b64encode( users.get_current_user().email() ) )
        else:
            self.url = users.create_login_url( self.request.uri )
            self.url_linktext = 'iniciar sesión'
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
    
    def get_ultimas_respuestas(self):
        respuestas = memcache.get('ultimas-respuestas')
        if respuestas is None:
            respuestas = db.GqlQuery("SELECT * FROM Respuesta ORDER BY fecha DESC").fetch(20)
            respuestas.reverse()
            if memcache.add('ultimas-respuestas', respuestas):
                logging.info('Almacenando ultimas-respuestas en memcache')
            else:
                logging.warning('Fallo al rellenar memcache con las preguntas ultimas-respuestas')
        else:
            logging.info('Leyendo ultimas-respuestas de memcache')
        return respuestas
    
    # devuelve un string con todas las etiquetas de un mixto separadas por comas
    def get_tags_from_mixto(self, mixto):
        retorno = ''
        listags = ['ubuntu']
        for m in mixto:
            try:
                tags = str(m.get('tags', '')).split(', ')
                for t in tags:
                    if t not in listags:
                        listags.append(t)
            except:
                pass
        for t in listags:
            if retorno == '':
                retorno = t
            else:
                retorno += ', ' + t
        return retorno
    
    # devuelve un string con todas las etiquetas de una lista separadas por comas
    def get_tags_from_list(self, elementos):
        retorno = ''
        listags = ['ubuntu']
        for e in elementos:
            tags = e.tags.split(', ')
            for t in tags:
                if t not in listags and t.strip() != '':
                    listags.append(t)
        for t in listags:
            if retorno == '':
                retorno = t
            else:
                retorno += ', ' + t
        return retorno
    
    # devuelve las paginas relacionadas con alguno de los tags del enlace
    def paginas_relacionadas(self, cadena, todas = False):
        retorno = []
        try:
            tags = str(cadena).split(', ')
            if len(tags) > 1:
                intentos = 4
                while intentos > 0 and len(retorno) < 10:
                    query = db.GqlQuery("SELECT * FROM Busqueda WHERE tag = :1 ORDER BY clics DESC", random.choice( tags ))
                    if todas:
                        aux = query.fetch( query.count() )
                    else:
                        aux = query.fetch(20)
                    if aux:
                        for elem in aux:
                            encontrado = False
                            for r in retorno:
                                if elem.url == r.url:
                                    encontrado = True
                            if not encontrado:
                                retorno.append( elem )
                    intentos -= 1
            elif len(tags) == 1:
                query = db.GqlQuery("SELECT * FROM Busqueda WHERE tag = :1 ORDER BY clics DESC", tags[0])
                if todas:
                    retorno = query.fetch( query.count() )
                else:
                    retorno = query.fetch(20)
        except:
            pass
        return retorno
    
    def get_notificaciones(self):
        if users.get_current_user():
            usuario = users.get_current_user()
            notis = memcache.get('notificaciones_' + str(usuario))
            if notis is None:
                notis = db.GqlQuery("SELECT * FROM Notificacion WHERE usuario = :1 ORDER BY fecha DESC", usuario).fetch(20)
                memcache.add('notificaciones_' + str(usuario), notis)
            else:
                logging.info('Leyendo notificaciones_' + str(usuario) + ' de memcache')
            return notis
        else:
            return []
    
    def search_job(self, query):
        retorno = []
        aux = db.GqlQuery("SELECT * FROM Busqueda WHERE tag = :1 ORDER BY clics DESC", query)
        if aux.count() > 0:
            retorno = aux.fetch( aux.count() )
        else:
            consulta = db.GqlQuery("SELECT * FROM Pregunta")
            preguntas = consulta.fetch(20, random.randint(0, max(0, consulta.count()-20)))
            for p in preguntas:
                p.get_tags()
                if p.tags.find(query) != -1:
                    try:
                        busq = Busqueda()
                        busq.url = '/question/' + str(p.key())
                        busq.text = p.titulo
                        busq.clics = p.visitas
                        busq.tag = query
                        busq.put()
                        logging.info('Añadida la url: ' + busq.url)
                        retorno.append(busq)
                    except:
                        logging.warning("Imposible guardar en busqueda la url: " + busq.url)
        return retorno
    
    def buscar(self, query=''):
        try:
            query = query.lower().strip()
        except:
            query = ''
        if len(query) > 1:
            # cargamos los tags
            all_tags = memcache.get('all-tags')
            if all_tags is None:
                all_tags = []
                for tag in KEYWORD_LIST:
                    all_tags.append([tag.lower(), 0])
            # añadimos la busqueda a la lista de tags
            found = False
            for tag in all_tags:
                if tag[0] == query:
                    found = True
            if not found:
                all_tags.append([query, 0])
                memcache.replace('all-tags', all_tags)
            # añadimos la busqueda a la lista de busquedas
            all_searches = memcache.get('all-searches')
            if all_searches is not None:
                found = False
                for s in all_searches:
                    if s[0] == query:
                        s[1] += 1
                        found = True
                if not found:
                    all_searches.append([query, 1])
                memcache.replace('all-searches', all_searches)
            else:
                all_searches = [[query, 1]]
                memcache.add('all-searches', all_searches)
            # comprobamos la busqueda en memcache
            retorno = self.search_job(query)
            if not retorno:
                # si no hay resultados, comprobamos si la query contiene etiquetas ya utilizadas
                retorno = []
                for tag in all_tags:
                    logging.info("Comprobando sub-busqueda: " + tag[0])
                    if re.search('\\b'+tag[0]+'\\b', query):
                        logging.info("Anyadiendo sub-busqueda: " + tag[0])
                        aux = db.GqlQuery("SELECT * FROM Busqueda WHERE tag = :1 ORDER BY clics DESC", tag[0]).fetch(20)
                        if aux is not None:
                            for a in aux:
                                retorno.append(a)
            # filtramos duplicados y destacamos el resultado exacto
            if len(retorno) > 1:
                mix = []
                while len(retorno) > 0:
                    elemento = retorno[0]
                    for r in retorno:
                        if r.text.lower().find(query) != -1:
                            elemento = r
                            break
                        elif r.clics > elemento.clics:
                            elemento = r
                    encontrado = False
                    for m in mix:
                        if m.url == elemento.url:
                            encontrado = True
                    if not encontrado:
                        mix.append(elemento)
                    retorno.remove(elemento)
                retorno = mix
            return retorno
