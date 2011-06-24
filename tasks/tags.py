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

import logging, random
from google.appengine.ext import db
from google.appengine.api import memcache
from base import *

class tags:
    def __init__(self):
        # diccionario que almacena todos los tags
        self.pendientes = {}
        
        # lista general de tags
        self.alltags = memcache.get('all-tags')
        if self.alltags is None:
            self.alltags = []
            self.alltags_memcache = False
        else:
            self.alltags_memcache = True
        
        # elegimos aleatoriamente una tabla
        for i in range(3):
            if self.seleccionar_tarea( random.randint(0, 2) ):
                break;
        
    def seleccionar_tarea(self, tabla):
        retorno = False
        if tabla == 0 and len(self.alltags) > 1: # all-tags
            logging.info('Actualizando all-tags')
            for t in range(20):
                num = random.randint(0, len(self.alltags)-1)
                elementos = memcache.get('tag_' + self.alltags[num][0])
                if elementos is None:
                    self.alltags.remove( self.alltags[num] )
                else:
                    self.alltags[num][1] = len( elementos )
            memcache.replace('all-tags', self.alltags)
            retorno = True
        else:
            if tabla == 1:
                query = db.GqlQuery("SELECT * FROM Pregunta")
                logging.info('Actualizando tags de preguntas')
            else:
                query = db.GqlQuery("SELECT * FROM Enlace")
                logging.info('Actualizando tags de enlaces')
            total = query.count()
            seleccion = query.fetch(20, random.randint(0, max(0, total-1)))
            if len(seleccion) > 0:
                for ele in seleccion:
                    if tabla == 1:
                        tags = self.tag2list( ele.tags )
                        link = '/question/' + str(ele.key())
                        title = ele.titulo
                        clics = ele.visitas
                    else:
                        tags = self.tag2list( ele.tags )
                        link = '/story/' + str(ele.key())
                        title = ele.descripcion
                        clics = ele.clicks
                    self.procesar(tags, link, title, clics)
                # actualizamos los datos de memcache
                self.actualizar()
                retorno = True
        return retorno
    
    # a partir de un string de tags, devuelve una lista de cada uno de ellos
    def tag2list(self, tags):
        try:
            return tags.split(', ')
        except:
            return ['general']
    
    # rellena pendientes con cada elemento, en funcion del tag
    def procesar(self, tags, link, title, clics):
        elemento = {'link': link, 'title': title, 'clics': clics}
        for t in tags:
            if t in self.pendientes:
                encontrado = False
                for p in self.pendientes[t]:
                    if p.get('link', '')  == link:
                        p['title'] = title
                        p['clics'] = clics
                        encontrado = True
                if not encontrado:
                    self.pendientes[t].append( elemento )
            else:
                elementos_cache = memcache.get('tag_' + t)
                if elementos_cache is None:
                    self.pendientes[t] = [elemento]
                else:
                    self.pendientes[t] = elementos_cache
                    if elemento not in self.pendientes[t]:
                        self.pendientes[t].append( elemento )
    
    # reducimos el numero de elementos por tag, en funcion de los clics
    def reducir(self, elementos):
        reducido = []
        for i in range(25):
            seleccionado = {'clics': -1}
            for e in elementos:
                if e not in reducido and e.get('clics', 0) > seleccionado.get('clics', 0):
                    seleccionado = e
            if seleccionado != {'clics': -1}:
                duplicado = False
                for e in reducido:
                    if e.get('link', '') == seleccionado.get('link', ''):
                        duplicado = True
                if not duplicado:
                    reducido.append( seleccionado )
        return reducido
    
    # actualiza los elementos de memcache con los nuevos resultados obtenidos
    def actualizar(self):
        for tag in self.pendientes.keys():
            elementos = self.reducir( self.pendientes[tag] )
            if elementos:
                if memcache.get('tag_' + tag) is None:
                    if memcache.add('tag_' + tag, elementos):
                        logging.info('Almacenados los resultados del tag ' + tag + ' en memcache')
                    else:
                        logging.error('Fallo al almacenar los resultados del tag ' + tag + ' en memcache')
                else:
                    if memcache.replace('tag_' + tag, elementos):
                        logging.info('Reemplazados los resultados del tag ' + tag + ' en memcache')
                    else:
                        logging.error('Fallo al reemplazar los resultados del tag ' + tag + ' en memcache')
            else:
                logging.error('Para el tag: ' + tag + ' no hay elementos!')
            # actualizamos la lista general de tags
            encontrado = False
            for t in self.alltags:
                if t[0] == tag:
                    t[1] = max(len(elementos), t[1])
                    encontrado = True
            if not encontrado:
                self.alltags.append([tag, 1])
        if not self.alltags_memcache:
            memcache.add('all-tags', self.alltags)
        else:
            memcache.replace('all-tags', self.alltags)

if __name__ == "__main__":
    tags()

