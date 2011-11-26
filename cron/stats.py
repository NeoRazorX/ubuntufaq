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

class stats:
    sc = Super_cache()
    
    def __init__(self):
        # leemos de memcache
        continuar = True
        stats = memcache.get( 'stats' )
        if stats is None:
            stats = {'iterador': 0,
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
            if memcache.add('stats', stats):
                logging.info("Almacenado stats en memcache")
            else:
                logging.error("Imposible almacenar stats en memcache")
                continuar = False
        else:
            logging.info("Lellendo stats desde memcache")
        
        # actualizamos el número de preguntas
        if stats['iterador'] == 0 and continuar:
            stats['preguntas'] = Pregunta.all(keys_only=True).count(999999)
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a las preguntas")
            continuar = False
        
        # actualizamos el número de respuestas
        if stats['iterador'] == 1 and continuar:
            stats['respuestas'] = Respuesta.all(keys_only=True).count(999999)
            if stats['preguntas'] > 0 and stats['respuestas'] > 0:
                stats['rpp'] = (float(stats['respuestas']) / stats['preguntas'])
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a las respuestas")
            continuar = False
        
        # actualizamos el número de enlaces
        if stats['iterador'] == 2 and continuar:
            stats['enlaces'] = Enlace.all(keys_only=True).count(999999)
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los enlaces")
            continuar = False
        
        # actualizamos el número de comentarios
        if stats['iterador'] == 3 and continuar:
            stats['comentarios'] = Comentario.all(keys_only=True).count(999999)
            if stats['enlaces'] > 0 and stats['comentarios'] > 0:
                stats['cpe'] = (float(stats['comentarios']) / stats['enlaces'])
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los comentarios")
            continuar = False
        
        # actualizamos el número de usuarios
        if stats['iterador'] == 4 and continuar:
            stats['usuarios'] = Usuario.all(keys_only=True).count(999999)
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los usuarios")
            continuar = False
        
        # actualizamos el número de seguimientos
        if stats['iterador'] == 5 and continuar:
            stats['seguimientos'] = Seguimiento.all(keys_only=True).count(999999)
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los seguimientos")
            continuar = False
        
        # actualizamos el top de usuarios
        if stats['iterador'] == 6 and continuar:
            # probamos con las preguntas
            preguntas = self.sc.get_preguntas()
            stats['tu_puntos'] = 0
            for p in preguntas:
                if p.puntos > stats['tu_puntos']:
                    stats['top_user'] = p.autor
                    stats['tu_puntos'] = p.puntos
            # probamos con los enlaces
            enlaces = self.sc.get_enlaces()
            for e in enlaces:
                if e.puntos > stats['tu_puntos']:
                    stats['top_user'] = e.autor
                    stats['tu_puntos'] = e.puntos
            stats['iterador'] = 0
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base al top_user")
            continuar = False

if __name__ == "__main__":
    stats()
