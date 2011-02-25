#!/usr/bin/env python

import logging, random
from google.appengine.ext import db
from google.appengine.api import users, memcache
from base import *

class karma:
    def __init__(self):
        # elegimos aleatoriamente una tabla
        eleccion = random.randint(0, 3)
        
        if eleccion == 0:
            seleccion = db.GqlQuery("SELECT * FROM Enlace WHERE puntos = 0").fetch(25)
        elif eleccion == 1:
            seleccion = db.GqlQuery("SELECT * FROM Comentario WHERE puntos = 0").fetch(25)
        elif eleccion == 2:
            seleccion = db.GqlQuery("SELECT * FROM Pregunta WHERE puntos = 0").fetch(25)
        else:
            seleccion = db.GqlQuery("SELECT * FROM Respuesta WHERE puntos = 0").fetch(25)
        
        if len( seleccion ) > 0:
            # marcamos los anonimos y seleccionamos los autores
            autores = []
            for usu1 in seleccion:
                if usu1.autor == None:
                    usu1.puntos = -1
                    usu1.put()
                elif usu1.autor not in autores:
                    autores.append( usu1.autor )
            
            # elegimos aleatoriamente un elemento
            if len( autores ) > 1:
                self.calcular( autores[random.randint(0, len( autores ) - 1)] )
            elif len( autores ) == 1:
                self.calcular( autores.pop() )
            else:
                logging.info("No se ha encontrado ningun usuario al que actualizar el karma")
        else:
            logging.info("No hay suficientes elementos en la seleccion inicial")
    
    def calcular(self, autor):
        if autor:
            # leemos de memcache
            continuar = True
            karma = memcache.get( 'usuario_' + str(autor) )
            if karma is not None:
                logging.info("Lellendo karma del usuario " + str(autor) + ' desde memcache')
            else:
                karma = {'puntos': 0,
                    'preguntas': False,
                    'respuestas': False,
                    'enlaces': False,
                    'comentarios': False
                }
                if not memcache.add( 'usuario_' + str(autor), karma, 86400 ):
                    logging.error("Imposible almacenar el karma del usuario " + str(autor) + ' en memcache')
                    continuar = False
                else:
                    logging.info("Almacenado el karma del usuario " + str(autor) + ' en memcache')
            
            if not karma['preguntas'] and continuar:
                query = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1", autor)
                karma['puntos'] += query.count()
                karma['preguntas'] = True
                memcache.replace( 'usuario_' + str(autor), karma, 86400 )
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las preguntas')
                continuar = False
            
            if not karma['respuestas'] and continuar:
                query = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1", autor)
                karma['puntos'] += query.count()
                karma['respuestas'] = True
                memcache.replace( 'usuario_' + str(autor), karma, 86400 )
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las respuestas')
                continuar = False
            
            if not karma['enlaces'] and continuar:
                query = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1", autor)
                karma['puntos'] += query.count()
                karma['enlaces'] = True
                memcache.replace( 'usuario_' + str(autor), karma, 86400 )
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a los enlaces')
                continuar = False
            
            if not karma['comentarios'] and continuar:
                query = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1", autor)
                karma['puntos'] += query.count()
                karma['comentarios'] = True
                memcache.replace( 'usuario_' + str(autor), karma, 86400 )
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a los comentarios')
                continuar = False
            
            if karma['preguntas'] and karma['respuestas'] and karma['enlaces'] and karma['comentarios'] and continuar:
                self.actualizar(autor, karma['puntos'])
        else:
            logging.info("El elemento seleccionado pertenece a un usuario anonimo")
    
    def actualizar(self, autor, puntos):
        # elegimos aleatoriamente una tabla
        eleccion = random.randint(0, 3)
        
        if eleccion == 0:
            seleccion = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1 AND puntos != :2", autor, puntos).fetch(20)
        elif eleccion == 1:
            seleccion = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1 AND puntos != :2", autor, puntos).fetch(20)
        elif eleccion == 2:
            seleccion = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1 AND puntos != :2", autor, puntos).fetch(20)
        else:
            seleccion = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1 AND puntos != :2", autor, puntos).fetch(20)
        
        try:
            # modificamos cada registro
            if seleccion:
                for ele in seleccion:
                    ele.puntos = puntos
                    ele.put()
                logging.info("Actualizado el karma del usuario")
            else:
                logging.info("No hay registros para actualizar (tabla: " + str(eleccion) + ")")
        except:
            logging.error("Imposible actualizar el karma del usuario")

if __name__ == "__main__":
    karma()

