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
APP_DOMAIN = 'http://www.ubufaq.com'
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
from datetime import datetime, timedelta


class Super_cache():
    listap = []
    listae = []
    ultimasr = False
    ultimosc = False
    alltags = False
    allsearches = False
    stats = False
    
    # obtiene el diccionario de conflictos de memcache
    # el diccionario de conflictos tiene una entrada para cada elemento
    # en conflicto (la key() del elemento en bigtable) y contiene una lista
    # con los identificadores de las instancias que tienen sus datos actualizados
    def get_conflictos(self):
        conflictos = memcache.get('conflictos')
        if conflictos is None:
            conflictos = {}
            if not memcache.add('conflictos', conflictos):
                logging.warning('Imposible anyadir diccionario de conflictos a memcache!')
        else:
            logging.info('Leyendo diccionario de conflictos de memcache')
        return conflictos
    
    # añade una entrada para ekey con el identificador de la instancia al diccionario de conflictos
    def add_conflicto(self, ekey):
        if ekey:
            cs = self.get_conflictos()
            cs[ekey] = [id(self)]
            if memcache.replace('conflictos', cs):
                logging.info('Anyadido conflicto en ' + ekey)
            else:
                logging.warning('Imposible reemplazar conflictos en memcache!')
    
    # conprueba en el diccionario de conflictos si hay que recargar el elemento con key = ekey
    def hay_conflicto_en(self, ekey):
        if ekey:
            cs = self.get_conflictos()
            lista = cs.get(ekey, [])
            if len(lista) < 1 or id(self) in lista:
                return False
            else:
                lista.append( id(self) )
                cs[ekey] = lista
                if memcache.replace('conflictos', cs):
                    logging.info('Actualizado diccionario de conflictos para ' + ekey)
                else:
                    logging.warning('Imposible actualizar el diccionario de conflictos en memcache!')
                return True
    
    def get_preguntas(self):
        if len(self.listap) < 1:
            logging.info('Generando lista_preguntas...')
            # ultimas preguntas
            self.listap = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(100)
            if not self.listap:
                self.listap = []
            # preguntas sin solucionar
            aux = db.GqlQuery("SELECT * FROM Pregunta WHERE estado in :1 ORDER BY estado ASC", [0, 1, 2, 3, 11]).fetch(100)
            if aux:
                for a in aux:
                    encontrado = False
                    for p in self.listap:
                        if p.key() == a.key():
                            encontrado = True
                            break
                    if not encontrado:
                        self.listap.append(a)
                        logging.info('Anyadiendo pregunta ' + a.get_link() + ' a memoria!')
        else:
            logging.info('Leyendo lista_preguntas de memoria')
        return self.listap
    
    def get_preguntas_sin_solucionar(self):
        retorno = []
        listap = self.get_preguntas()
        for estado in [0, 1, 2, 3, 11]:
            for p in listap:
                if p.estado == estado:
                    retorno.append(p)
        return retorno
    
    def get_pregunta(self, idp, ip = None):
        pregunta = False
        if idp:
            listap = self.get_preguntas()
            num = 0
            while num < len(listap):
                if str(listap[num].key()) == idp:
                    if self.hay_conflicto_en(idp):
                        listap.remove(listap[num])
                        logging.info('Pregunta eliminada de la memoria por conflicto!')
                    else:
                        pregunta = listap[num]
                        logging.info('Encontrada la pregunta '+pregunta.get_link()+' en memoria!')
                        if ip and (pregunta.ultima_ip != ip or ip == '127.0.0.1'):
                            pregunta.ultima_ip = ip
                            pregunta.visitas += 1
                            if pregunta.visitas % 10 == 0:
                                try:
                                    pregunta.put()
                                    logging.info('Actualizada la pregunta ' + pregunta.get_link())
                                    self.add_conflicto(idp)
                                except:
                                    logging.warning('Imposible actualizar las visitas de la pregunta ' + pregunta.get_link())
                    break
                num += 1
            if not pregunta:
                logging.info('Pregunta no encontrada en memoria!')
                try:
                    pregunta = Pregunta.get(idp)
                    if pregunta:
                        listap.append(pregunta)
                        logging.info('Anyadiendo pregunta '+pregunta.get_link()+' a memoria')
                    else:
                        logging.warning('Pregunta con id: '+idp+' no encontrada!')
                        pregunta = False
                except:
                    logging.warning('Error al buscar la pregunta con id: '+idp)
                    pregunta = False
        return pregunta
    
    def get_respuestas_de(self, idp):
        respuestas = []
        if idp:
            listap = self.get_preguntas()
            for p in listap:
                if str(p.key()) == idp:
                    respuestas = memcache.get(idp)
                    if respuestas is None:
                        query = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1 ORDER BY fecha ASC", idp)
                        respuestas = query.fetch( query.count() )
                        if not memcache.add(idp, respuestas):
                            logging.warning('Imposible almacenar en memcache las respuestas de: ' + p.get_link())
                    else:
                        logging.info('Leyendo de memcache las respuestas para: ' + p.get_link())
                    if p.respuestas != len(respuestas):
                        if len(respuestas) > p.respuestas:
                            det = Detector_respuestas()
                            det.detectar(respuestas, p.get_link())
                        p.respuestas = len(respuestas)
                        try:
                            p.put()
                            logging.info('Actualizado el num. de respuestas de ' + p.get_link())
                            self.add_conflicto(idp)
                        except:
                            logging.warning('Imposible actualizar el num. de respuestas de la pregunta: ' + p.get_link())
                    break
        return respuestas
    
    def borrar_cache_pregunta(self, idp):
        if idp:
            listap = self.get_preguntas()
            num = 0
            borrado = False
            while num < len(listap):
                if str(listap[num].key()) == idp:
                    listap.remove( listap[num] )
                    borrado = True
                    break
                num += 1
            if borrado:
                self.add_conflicto(idp)
                logging.info('Pregunta con id: ' + idp + ' borrada de la cache!')
            else:
                logging.info('Pregunta con id: ' + idp + ' no encontrada en la cache!')
    
    def get_enlaces(self):
        if len(self.listae) < 1:
            logging.info('Generando lista_enlaces...')
            self.listae = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(100)
            if not self.listae:
                self.listae = []
        else:
            logging.info('Leyendo lista_enlaces de memoria')
        return self.listae
    
    def get_enlace(self, ide, ip = None):
        enlace = False
        if ide:
            listae = self.get_enlaces()
            num = 0
            while num < len(listae):
                if str(listae[num].key()) == ide:
                    if self.hay_conflicto_en(ide):
                        listae.remove(listae[num])
                        logging.info('Enlace eliminado de la memoria por conflicto!')
                    else:
                        enlace = listae[num]
                        logging.info('Enlace '+enlace.get_link()+' encontrado en memoria!')
                        if ip and (enlace.ultima_ip != ip or ip == '127.0.0.1'):
                            enlace.ultima_ip = ip
                            enlace.clicks += 1
                            if enlace.clicks % 10 == 0:
                                try:
                                    enlace.put()
                                    logging.info('Enlace '+enlace.get_link()+' actualizado!')
                                    self.add_conflicto(ide)
                                except:
                                    logging.warning('Imposible actualizar las visitas del enlace: ' + enlace.get_link())
                    break
                num += 1
            if not enlace:
                logging.info('Enlace no encontrado en memoria!')
                try:
                    enlace = Enlace.get(ide)
                    if enlace:
                        listae.append(enlace)
                        logging.info('Anyadiendo enlace '+enlace.get_link()+' a lista_enlaces de memoria')
                    else:
                        enlace = False
                        logging.warning('Enlace con id: '+ide+' no encontrado!')
                except:
                    enlace = False
                    logging.warning('Error buscando enlace con id: '+ide)
        return enlace
    
    def get_comentarios_de(self, ide):
        comentarios = []
        if ide:
            listae = self.get_enlaces()
            for e in listae:
                if str(e.key()) == ide:
                    comentarios = memcache.get(ide)
                    if comentarios is None:
                        query = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", ide)
                        comentarios = query.fetch( query.count() )
                        if not memcache.add(ide, comentarios):
                            logging.warning('Imposible almacenar en memcache los comentarios de: ' + e.get_link())
                    else:
                        logging.info('Leyendo comentarios de memcache para: ' + e.get_link())
                    cambio = False
                    if e.comentarios != len( comentarios ):
                        if len(comentarios) > e.comentarios:
                            # añadimos las notificaciones pertinentes
                            if e.autor and len(comentarios) == 1:
                                try:
                                    n = Notificacion()
                                    n.usuario = e.autor
                                    n.link = e.get_link()
                                    n.mensaje = 'Han comentado tu enlace ' + e.descripcion[:99] + '...'
                                    n.put()
                                    n.borrar_cache()
                                except:
                                    logging.warning('Imposible guardar la notificación')
                            else:
                                det = Detector_respuestas()
                                det.detectar(comentarios, e.get_link())
                        e.comentarios = len(comentarios)
                        cambio = True
                    if not e.tags:
                        e.get_tags()
                        cambio = True
                    if cambio:
                        try:
                            e.put()
                            logging.info('Actualizado el num. de comentarios de ' + e.get_link())
                            self.add_conflicto(ide)
                        except:
                            logging.warning('Imposible actualizar num. de comentarios del enlace: ' + e.get_link())
                    break
        return comentarios
    
    def borrar_cache_enlace(self, ide):
        if ide:
            listae = self.get_enlaces()
            num = 0
            borado = False
            while num < len(listae):
                if str(listae[num].key()) == ide:
                    listae.remove( listae[num] )
                    borrado = True
                    break
                num += 1
            if borrado:
                self.add_conflicto(ide)
                logging.info('Enlace con id: ' + ide + ' borrado de la cache!')
            else:
                logging.info('Enlace con id: ' + ide + ' no encontrado en la cache!')
    
    def get_portada(self, usuario = False):
        preguntas = self.get_preguntas()[:]
        enlaces = self.get_enlaces()[:]
        mixto = []
        num_enlaces = 0
        max_pusuario = 2 # num. max. de preguntas del usuario
        max_eusuario = 2 # num. max. de enlaces del usuario
        while len(mixto) < 20 and (len(preguntas) > 0 or len(enlaces) > 0):
            elemento = False
            tipo = ''
            if usuario and (max_pusuario > 0 or max_eusuario > 0):
                if max_pusuario > 0:
                    # seleccionamos las ultimas preguntas del usuario (max. 7 días)
                    for p in preguntas:
                        if p.autor == usuario and p.fecha > (datetime.today() - timedelta(days=7)):
                            if not elemento:
                                elemento = p
                                tipo = 'pregunta'
                            elif p.fecha > elemento.fecha:
                                elemento = p
                                tipo = 'pregunta'
                    if not elemento:
                        max_pusuario = 0
                if max_eusuario > 0:
                    # seleccionamos los ultimos enlaces del usuario (max. 7 días)
                    for e in enlaces:
                        if e.autor == usuario and e.fecha > (datetime.today() - timedelta(days=7)):
                            if not elemento:
                                elemento = e
                                tipo = 'enlace'
                            elif e.fecha > elemento.fecha:
                                elemento = e
                                tipo = 'enlace'
                    if not elemento:
                        max_eusuario = 0
            else:
                # seleccionamos la pregunta mas apropiada
                num = 0
                while num < len(preguntas):
                    if preguntas[num].es_erronea():
                        preguntas.remove(preguntas[num])
                        num = 0
                    else:
                        if not elemento:
                            elemento = preguntas[num]
                            tipo = 'pregunta'
                        elif preguntas[num].fecha > elemento.fecha:
                            elemento = preguntas[num]
                            tipo = 'pregunta'
                        num += 1
                # seleccionamos el enlace mas apropiado
                for e in enlaces:
                    if not(elemento and tipo == 'pregunta' and len(mixto) > 8 and num_enlaces > 8):
                        if not elemento:
                            elemento = e
                            tipo = 'enlace'
                        elif e.fecha > elemento.fecha:
                            elemento = e
                            tipo = 'enlace'
                    num += 1
            # añadimos el elemento
            if elemento:
                if tipo == 'pregunta':
                    preguntas.remove( elemento )
                    if usuario and elemento.autor == usuario:
                        max_pusuario -= 1
                    mixto.append({'tipo': 'pregunta',
                            'key': elemento.key(),
                            'autor': elemento.autor,
                            'puntos': elemento.puntos,
                            'descripcion': elemento.contenido,
                            'clicks': elemento.visitas,
                            'creado': elemento.creado,
                            'fecha': elemento.fecha,
                            'comentarios': elemento.respuestas,
                            'titulo': elemento.titulo,
                            'estado': elemento.estado,
                            'link': elemento.get_link(),
                            'tags': elemento.tags})
                elif tipo == 'enlace':
                    enlaces.remove( elemento )
                    num_enlaces += 1
                    if usuario and elemento.autor == usuario:
                        max_eusuario -= 1
                    mixto.append({'tipo': elemento.tipo_enlace,
                            'key': elemento.key(),
                            'autor': elemento.autor,
                            'puntos': elemento.puntos,
                            'descripcion': elemento.descripcion,
                            'clicks': elemento.clicks,
                            'creado': elemento.creado,
                            'fecha': elemento.fecha,
                            'comentarios': elemento.comentarios,
                            'link': elemento.get_link(),
                            'tags': elemento.tags})
            else:
                max_eusuario = 0
        return mixto
    
    def get_populares(self):
        preguntas = self.get_preguntas()[:]
        enlaces = self.get_enlaces()[:]
        mixto = []
        while len(mixto) < 20 and (len(preguntas) > 0 or len(enlaces) > 0):
            elemento = False
            clics = 0
            # seleccionamos la pregunta mas apropiada
            num = 0
            while num < len(preguntas):
                if preguntas[num].es_erronea():
                    preguntas.remove(preguntas[num])
                    num = 0
                else:
                    if not elemento:
                        elemento = preguntas[num]
                        clics = elemento.visitas
                        tipo = 'pregunta'
                    elif preguntas[num].visitas > clics:
                        elemento = preguntas[num]
                        clics = elemento.visitas
                        tipo = 'pregunta'
                    num += 1
            # seleccionamos el enlace mas apropiado
            if len(enlaces) > 0:
                if not elemento:
                    elemento = enlaces[0]
                    clics = elemento.clicks
                    tipo = 'enlace'
                for e in enlaces:
                    if e.clicks > clics:
                        elemento = e
                        clics = elemento.clicks
                        tipo = 'enlace'
            # añadimos el elemento
            if elemento:
                if tipo == 'pregunta':
                    preguntas.remove( elemento )
                    mixto.append({'tipo': 'pregunta',
                            'key': elemento.key(),
                            'autor': elemento.autor,
                            'puntos': elemento.puntos,
                            'descripcion': elemento.contenido,
                            'clicks': elemento.visitas,
                            'creado': elemento.creado,
                            'fecha': elemento.fecha,
                            'comentarios': elemento.respuestas,
                            'titulo': elemento.titulo,
                            'estado': elemento.estado,
                            'link': elemento.get_link(),
                            'tags': elemento.tags})
                elif tipo == 'enlace':
                    enlaces.remove( elemento )
                    mixto.append({'tipo': elemento.tipo_enlace,
                            'key': elemento.key(),
                            'autor': elemento.autor,
                            'puntos': elemento.puntos,
                            'descripcion': elemento.descripcion,
                            'clicks': elemento.clicks,
                            'creado': elemento.creado,
                            'fecha': elemento.fecha,
                            'comentarios': elemento.comentarios,
                            'link': elemento.get_link(),
                            'tags': elemento.tags})
        return mixto
    
    def get_ultimas_respuestas(self):
        if not self.ultimasr or random.randint(0, 9) == 0:
            self.ultimasr = memcache.get('ultimas-respuestas')
            logging.info('Leyendo ultimas-respuestas de memcache')
        if self.ultimasr is None:
            logging.info('Generando ultimas-respuestas...')
            self.ultimasr = db.GqlQuery("SELECT * FROM Respuesta ORDER BY fecha DESC").fetch(20)
            self.ultimasr.reverse()
            if not memcache.add('ultimas-respuestas', self.ultimasr):
                logging.warning('Fallo al rellenar memcache con las ultimas-respuestas')
        else:
            logging.info('Leyendo ultimas respuestas de memoria')
        return self.ultimasr
    
    def get_ultimos_comentarios(self):
        if not self.ultimosc or random.randint(0, 9) == 0:
            self.ultimosc = memcache.get('ultimos-comentarios')
            logging.info('Leyendo ultimos comentarios de memcache')
        if self.ultimosc is None:
            logging.info('Generando ultimos-comentarios...')
            self.ultimosc = db.GqlQuery("SELECT * FROM Comentario ORDER BY fecha DESC").fetch(20)
            self.ultimosc.reverse()
            if not memcache.add('ultimas-comentarios', self.ultimosc):
                logging.warning('Fallo al rellenar memcache con las ultimas-comentarios')
        else:
            logging.info('Leyendo ultimos comentarios de memoria')
        return self.ultimosc
    
    def get_alltags(self):
        if not self.alltags or random.randint(0, 9) == 0:
            self.alltags = memcache.get('all-tags')
            logging.info('Leyendo all-tags de memcache')
        if self.alltags is None or len(self.alltags) < 1:
            logging.info('Generando all-tags...')
            self.alltags = []
            for tag in KEYWORD_LIST:
                self.alltags.append([tag.lower(), 0])
            if not memcache.add('all-tags', self.alltags):
                logging.warning('Fallo al rellenar memcache con los tags')
        else:
            logging.info('Leyendo all-tags de memoria')
        return self.alltags
    
    def set_tag(self, tag, num):
        if tag and num > 0:
            tags = self.get_alltags()
            for t in tags:
                if t[0] == tag:
                    t[1] = num
                    logging.info('Establecido el num. de elementos del tag: ' + tag.encode('ascii', 'ignore'))
                    break
    
    def get_allsearches(self):
        if not self.allsearches or random.randint(0, 9) == 0:
            self.allsearches = memcache.get('all-searches')
            logging.info('Leyendo all-searches de memcache')
        return self.allsearches
    
    def get_stats(self):
        if not self.stats or random.randint(0, 9) == 0:
            self.stats = memcache.get('stats')
            logging.info('Leyendo stats de memcache')
        if self.stats is None:
            self.stats = {'iterador': 0,
                    'preguntas': 0,
                    'preguntas_cache': 0,
                    'respuestas': 0,
                    'rpp': 0,
                    'enlaces': 0,
                    'enlaces_cache': 0,
                    'comentarios': 0,
                    'cpe': 0,
                    'usuarios': 0,
                    'seguimientos': 0,
                    'top_user': None,
                    'tu_puntos': 0,
                    'tags': 0,
                    'votos': 0
            }
            if not memcache.add('stats', self.stats):
                logging.warning('Imposible almacenar stats!')
        if not self.listap:
            self.stats['preguntas_cache'] = 0
        else:
            self.stats['preguntas_cache'] = len(self.listap)
            if self.stats['preguntas'] < len(self.listap):
                self.stats['preguntas'] = len(self.listap)
        if not self.listae:
            self.stats['enlaces_cache'] = 0
        else:
            self.stats['enlaces_cache'] = len(self.listae)
            if self.stats['enlaces'] < len(self.listae):
                self.stats['enlaces'] = len(self.listae)
        if not self.alltags:
            self.stats['tags'] = 0
        else:
            self.stats['tags'] = len(self.alltags)
        return self.stats
    
    # devuelve las paginas relacionadas con alguno de los tags del enlace
    def paginas_relacionadas(self, cadena, todas = False):
        retorno = []
        if cadena:
            try:
                tags = cadena.split(', ')
                if len(tags) > 1:
                    intentos = 4
                    while len(tags) > 0 and intentos > 0 and len(retorno) < 20:
                        eleccion = random.choice(tags)
                        tags.remove(eleccion)
                        aux = self.get_busqueda(eleccion)
                        if aux:
                            for elem in aux:
                                encontrado = False
                                for r in retorno:
                                    if elem.url == r.url:
                                        encontrado = True
                                        break
                                if not encontrado:
                                    if todas or len(retorno) < 20:
                                        retorno.append( elem )
                                    else:
                                        break
                        intentos -= 1
                elif len(tags) == 1:
                    aux = self.get_busqueda(tags[0])
                    if todas:
                        retorno = aux
                    else:
                        for a in aux:
                            if len(retorno) < 20:
                                retorno.append(a)
                            else:
                                break
            except:
                logging.warning('Imposible mostrar paginas relacionadas!')
        return retorno
    
    def get_busqueda(self, tag):
        busqueda = memcache.get('busqueda_'+tag)
        if busqueda is None:
            logging.info('Leyendo busqueda_'+tag.encode('ascii', 'ignore')+' de bigTable')
            busqueda = db.GqlQuery("SELECT * FROM Busqueda WHERE tag = :1 ORDER BY fecha DESC", tag).fetch(50)
            if busqueda:
                memcache.add('busqueda_'+tag, busqueda)
            else:
                busqueda = []
        else:
            logging.info('Leyendo busqueda_'+tag.encode('ascii', 'ignore')+' de memcache')
            self.set_tag(tag, len(busqueda))
        return busqueda
    
    def search_job(self, query):
        logging.info("Iniciando search_job para: " + query.encode('ascii', 'ignore'))
        retorno = self.get_busqueda(query)
        if not retorno:
            retorno = []
            preguntas = self.get_preguntas()
            for p in preguntas:
                p.get_tags()
                if p.tags.find(query) != -1:
                    try:
                        busq = Busqueda()
                        busq.url = '/question/' + str(p.key())
                        busq.text = p.titulo
                        busq.clics = p.visitas
                        busq.fecha = p.fecha
                        busq.tag = query
                        busq.put()
                        busq.borrar_cache()
                        logging.info('Anyadida la url: ' + busq.url)
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
            all_tags = self.get_alltags()
            # añadimos la busqueda a la lista de tags
            found = False
            for tag in all_tags:
                if tag[0] == query:
                    found = True
                    break
            if not found:
                all_tags.append([query, 0])
                memcache.replace('all-tags', all_tags)
            # añadimos la busqueda a la lista de busquedas
            all_searches = self.get_allsearches()
            if all_searches is not None:
                found = False
                for s in all_searches:
                    if s[0] == query:
                        s[1] += 1
                        found = True
                        break
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
                    logging.info("Comprobando sub-busqueda: " + tag[0].encode('ascii', 'ignore'))
                    if re.search('\\b'+tag[0]+'\\b', query):
                        logging.info("Anyadiendo sub-busqueda: " + tag[0].encode('ascii', 'ignore'))
                        aux = self.get_busqueda(tag[0])
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
                        elif r.fecha > elemento.fecha:
                            elemento = r
                    encontrado = False
                    for m in mix:
                        if m.url == elemento.url:
                            encontrado = True
                            break
                    if not encontrado:
                        mix.append(elemento)
                    retorno.remove(elemento)
                retorno = mix
            return retorno


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
                self.borrar_cache()
            except:
                logging.warning('Imposible actualizar la pregunta: ' + str(self.key()) )
        if len( seguimiento ) == 0:
            return None
        else:
            return seguimiento[0]
    
    def get_tags(self, all_tags = []):
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
    
    def esta_solucionada(self):
        if self.estado in [10, 12, 13, 14]:
            return True
        else:
            return False
    
    def es_erronea(self):
        if self.estado in [12, 13, 14]:
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
                    logging.error('Imposible guardar la notificacion')
        # guardamos los cambios
        self.put()
        self.borrar_cache()
    
    def marcar_pendiente(self):
        self.estado = 11
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
                logging.error('Imposible guardar la notificacion')
    
    def marcar_solucionada(self):
        self.estado = 10
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
                logging.error('Imposible guardar la notificacion')
    
    def borrar_respuestas(self):
        r = Respuesta.all().filter('id_pregunta =', self.key())
        db.delete(r)
    
    def borrar_seguimiento(self):
        s = db.GqlQuery("SELECT * FROM Seguimiento WHERE id_pregunta = :1", str(self.key()))
        db.delete(s)
    
    def borrar_busquedas(self):
        b = db.GqlQuery("SELECT * FROM Busqueda WHERE url = :1", self.get_link())
        db.delete(b)
        try:
            tags = str(self.tags).split(', ')
            for t in tags:
                memcache.delete('busqueda_'+t)
        except:
            pass
    
    # borramos la cache que contenga esta pregunta
    def borrar_cache(self):
        memcache.delete_multi([str(self.key()), 'seguimiento_'+str(self.key()), 'ultimas-respuestas'])
        logging.info('Borrada toda la cache que haga referencia a la pregunta: ' + self.get_link())
    
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
    
    def get_link(self):
        return '/question/' + self.id_pregunta + '#' + str(self.key())
    
    def get_ip(self):
        try:
            return self.ips[0]
        except:
            return None
    
    def borrar_cache(self):
        memcache.delete_multi([self.id_pregunta, 'ultimas-respuestas'])


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
    
    def nuevo(self, alltags = []):
        if not self.tags:
            self.get_tags(alltags)
        self.put()
        self.comprobar()
    
    def comprobar(self):
        cambio = False
        if self.url is None:
            self.url = self.get_full_link()
            cambio = True
        if self.tipo_enlace is None:
            if self.url[:23] == 'http://www.youtube.com/':
                self.tipo_enlace = 'youtube'
            elif self.url[:21] == 'http://www.vimeo.com/':
                self.tipo_enlace = 'vimeo'
            elif self.url[-4:] in ['.ogv', '.OGV', '.mp4', '.MP4'] or self.url[-5:] in ['.webm', '.WEBM']:
                self.tipo_enlace = 'vhtml5'
            elif self.url[-4:] in ['.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF'] or self.url[-5:] in ['.jpeg', '.JPEG']:
                self.tipo_enlace = 'imagen'
            elif self.url[-4:] in ['.deb', '.DEB']:
                self.tipo_enlace = 'deb'
            elif self.url[-4:] in ['.deb', '.DEB', '.tgz', '.TGZ', '.bz2', '.BZ2'] or self.url[-3:] in ['.gz', '.GZ']:
                self.tipo_enlace = 'package'
            else:
                self.tipo_enlace = 'texto'
            cambio = True
        if cambio:
            self.put()
    
    def get_link(self):
        return '/story/' + str(self.key())
    
    def get_full_link(self):
        return APP_DOMAIN + '/story/' + str(self.key())
    
    def get_tags(self, all_tags = []):
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
        logging.warning('Se ha hundido el enlace con id: ' + str(self.key()))
        self.borrar_cache()
    
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
        try:
            tags = str(self.tags).split(', ')
            for t in tags:
                memcache.delete('busqueda_'+t)
        except:
            pass
    
    # borramos la cache que contenga este enlace
    def borrar_cache(self):
        memcache.delete_multi([str(self.key()), 'ultimos-comentarios'])
        logging.info('Borrada toda la cache que haga referencia al enlace: ' + self.get_link())
    
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
    ips = db.StringListProperty()
    os = db.StringProperty(default="desconocido")
    puntos = db.IntegerProperty(default=0)
    valoracion = db.IntegerProperty(default=0)
    
    def get_link(self):
        return '/story/' + self.id_enlace + '#' + str(self.key())
    
    def get_ip(self):
        try:
            return self.ips[0]
        except:
            return None
    
    def borrar_cache(self):
        memcache.delete_multi([self.id_enlace, 'ultimos-comentarios'])


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
                        logging.error('Imposible guardar la notificacion')
                i -= 1


class Busqueda(db.Model):
    clics = db.IntegerProperty(default=0)
    fecha = db.DateTimeProperty(auto_now_add=True)
    tag = db.StringProperty()
    text = db.StringProperty()
    url = db.StringProperty()
    
    def borrar_cache(self):
        memcache.delete('busqueda_' + self.tag)


# clase para gestionar el siguimiento de preguntas
class Seguimiento(db.Model):
    estado = db.IntegerProperty(default=0)
    id_pregunta = db.StringProperty()
    respuestas = db.IntegerProperty(default=0)
    usuarios = db.ListProperty( users.User )
    
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
    sc = Super_cache()
    
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
    
    def extraer_tags(self, texto):
        retorno = ''
        all_tags = self.sc.get_tags()
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
        if elementos:
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
