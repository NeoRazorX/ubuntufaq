#!/usr/bin/env python

import logging, random
from google.appengine.ext import db
from google.appengine.api import memcache
from base import *

class stats:
    def __init__(self):
        # leemos de memcache
        continuar = True
        stats = memcache.get( 'stats' )
        if stats is not None:
            logging.info("Lellendo stats desde memcache")
        else:
            stats = {'iterador': 0,
                    'preguntas': 0,
                    'respuestas': 0,
                    'rpp': 0,
                    'enlaces': 0,
                    'comentarios': 0,
                    'cpe': 0,
                    'clics_p': 0,
                    'clics_pp': 0,
                    'clics_e': 0,
                    'clics_pe': 0,
                    'top_user': None,
                    'tu_puntos': 0
            }
            if not memcache.add('stats', stats):
                logging.error("Imposible almacenar stats en memcache")
                continuar = False
            else:
                logging.info("Almacenado stats en memcache")
        
        # actualizamos el numero de preguntas
        if stats['iterador'] == 0 and continuar:
            query = db.GqlQuery("SELECT * FROM Pregunta")
            stats['preguntas'] = query.count()
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a las preguntas")
            continuar = False
        
        # actualizamos el numero de respuestas
        if stats['iterador'] == 1 and continuar:
            query = db.GqlQuery("SELECT * FROM Respuesta")
            stats['respuestas'] = query.count()
            if stats['preguntas'] > 0 and stats['respuestas'] > 0:
                stats['rpp'] = (stats['respuestas'] / stats['preguntas'])
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a las respuestas")
            continuar = False
        
        # actualizamos el numero de enlaces
        if stats['iterador'] == 2 and continuar:
            query = db.GqlQuery("SELECT * FROM Enlace")
            stats['enlaces'] = query.count()
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los enlaces")
            continuar = False
        
        # actualizamos el numero de comentarios
        if stats['iterador'] == 3 and continuar:
            query = db.GqlQuery("SELECT * FROM Comentario")
            stats['comentarios'] = query.count()
            if stats['enlaces'] > 0 and stats['comentarios'] > 0:
                stats['cpe'] = (stats['comentarios'] / stats['enlaces'])
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los comentarios")
            continuar = False
        
        # actualizamos el numero de clics por pregunta
        if stats['iterador'] == 4 and continuar:
            query = db.GqlQuery("SELECT * FROM Pregunta")
            stats['clics_p'] = 0
            for p in query:
                stats['clics_p'] += p.visitas
            if stats['preguntas'] > 0 and stats['clics_p'] > 0:
                stats['clics_pp'] = (stats['clics_p'] / stats['preguntas'])
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los clics por pregunta")
            continuar = False
        
        # actualizamos el numero de clics por enlace
        if stats['iterador'] == 5 and continuar:
            query = db.GqlQuery("SELECT * FROM Enlace")
            stats['clics_e'] = 0
            for e in query:
                stats['clics_e'] += e.clicks
            if stats['enlaces'] > 0 and stats['clics_e'] > 0:
                stats['clics_pe'] = (stats['clics_e'] / stats['enlaces'])
            stats['iterador'] += 1
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base a los clics por enlace")
            continuar = False
        
        # actualizamos el numero de clics por enlace
        if stats['iterador'] == 6 and continuar:
            populares = memcache.get( 'populares' )
            stats['tu_puntos'] = 0
            if populares is not None:
                for p in populares:
                    if p['puntos'] > stats['tu_puntos']:
                        stats['top_user'] = p['autor']
                        stats['tu_puntos'] = p['puntos']
            stats['iterador'] = 0
            memcache.replace('stats', stats)
            logging.info("Actualizado stats en base al top_user")
            continuar = False

if __name__ == "__main__":
    stats()
