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

import logging, random
from google.appengine.ext import db
from google.appengine.api import memcache
from base import *

class Buscar:
    def __init__(self):
        # diccionario que almacena todos los tags
        self.pendientes = {}
        # lista general de tags
        self.alltags = memcache.get('all-tags')
        if self.alltags is None:
            self.alltags_memcache = False
            self.alltags = []
            for tag in KEYWORD_LIST:
                self.alltags.append([tag.lower(), 0])
        else:
            # eliminamos los tags vacios y los duplicados
            unicos = []
            for tag in self.alltags:
                if tag[0].strip() != '':
                    found = False
                    for ntag in unicos:
                        if tag[0] == ntag[0]:
                            found = True
                    if not found:
                        unicos.append([ tag[0], tag[1] ])
            self.alltags = unicos
            self.alltags_memcache = True
        # elegimos aleatoriamente una tabla
        for i in range(2):
            if self.seleccionar_tarea( random.randint(0, 1) ):
                break;
    
    def seleccionar_tarea(self, tabla):
        retorno = False
        if tabla == 0:
            query = db.GqlQuery("SELECT * FROM Pregunta")
            logging.info('Comprobando tags de preguntas')
        else:
            query = db.GqlQuery("SELECT * FROM Enlace")
            logging.info('Comprobando tags de enlaces')
        total = query.count()
        seleccion = query.fetch(5, random.randint(0, max(0, total-5)))
        if len(seleccion) > 0:
            for ele in seleccion:
                # actualizamos los tags
                tag0 = ele.tags
                ele.get_tags()
                if ele.tags != tag0:
                    try:
                        ele.put()
                        logging.info("Actualizados tags de " + ele.get_link())
                    except:
                        logging.warning("Imposible actualizar tags de " + ele.get_link())
                # agrupamos los datos necesarios
                if tabla == 0:
                    tags = self.tag2list(ele.tags)
                    link = ele.get_link()
                    title = ele.titulo
                    clics = ele.visitas
                else:
                    tags = self.tag2list(ele.tags)
                    link = ele.get_link()
                    title = ele.descripcion
                    clics = ele.clicks
                self.procesar(tags, link, title, clics)
            # actualizamos los resultados de las búsquedas
            self.actualizar()
            retorno = True
        return retorno
    
    # a partir de un string de tags, devuelve una lista de cada uno de ellos
    def tag2list(self, tags):
        try:
            retorno = []
            found_tags = tags.split(', ')
            if len(found_tags) > 0:
                # eliminamos duplicados
                for tag in found_tags:
                    if tag.strip() != '' and tag not in retorno:
                        retorno.append(tag)
                    encontrado = False
                    for otag in self.alltags:
                        if otag[0] == tag:
                            encontrado = True
                    if not encontrado:
                        self.alltags.append([tag, 1])
        except:
            retorno = []
        return retorno
    
    # rellena pendientes con cada elemento, en funcion del tag
    def procesar(self, tags, link, title, clics):
        for t in tags:
            logging.info('Comprobando el tag: ' + t)
            if t not in self.pendientes:
                logging.info('No hay pendientes para: ' + t)
                query = db.GqlQuery("SELECT * FROM Busqueda WHERE tag = :1", t)
                elementos_cache = query.fetch( query.count() )
                if elementos_cache:
                    self.pendientes[t] = elementos_cache
                else:
                    self.pendientes[t] = []
            logging.info('Hay '+str(len(self.pendientes[t]))+' pendientes para: ' + t)
            encontrado = False
            for p in self.pendientes[t]:
                if p.url  == link:
                    encontrado = True
                    if p.text != title or p.clics != clics:
                        p.text = title
                        p.clics = clics
                        try:
                            p.put()
                            logging.info('Actualizada la url: ' + p.url)
                        except:
                            logging.warning("Imposible modificar el enlace a: " + p.url)
            if not encontrado:
                try:
                    busq = Busqueda()
                    busq.url = link
                    busq.text = title
                    busq.clics = clics
                    busq.tag = t
                    busq.put()
                    self.pendientes[t].append( busq )
                    logging.info('Añadida la url: ' + busq.url)
                except:
                    logging.warning("Imposible guardar en busqueda la url: " + busq.url)
    
    # actualiza los elementos de memcache con los nuevos resultados obtenidos
    def actualizar(self):
        for tag in self.alltags:
            nume = len( self.pendientes.get(tag[0], []) )
            if nume > 0:
                tag[1] = nume
        if not self.alltags_memcache:
            memcache.add('all-tags', self.alltags)
        else:
            memcache.replace('all-tags', self.alltags)

if __name__ == "__main__":
    Buscar()
