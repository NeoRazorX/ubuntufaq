#!/usr/bin/env python

import logging, random
from google.appengine.ext import db
from google.appengine.api import users
from base import *

class karma:
    def paginar(self, consulta):
        total = consulta.count()
        if consulta.count() > 10:
            eleccion = random.randint(0, total - 1)
        else:
            eleccion = 0
        
        return consulta.fetch( 10, eleccion ), total
    
    def calcular(self, autor):
        if autor:
            logging.info("Calculando el karma del usuario " + str(autor))
            
            # obtenemos los ultimos registros del usuario
            try:
                q_preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1", autor)
                q_respuestas = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1", autor)
                q_enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1", autor)
                q_comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1", autor)
                
                # paginamos a la vez que calculamos el karma
                caca = 0
                preguntas, caca = self.paginar( q_preguntas )
                respuestas, caca = self.paginar( q_respuestas )
                puntos = 1 + caca
                enlaces, caca = self.paginar( q_enlaces )
                puntos += caca
                comentarios, caca = self.paginar( q_comentarios )
                puntos += caca
            except:
                logging.error("Imposible obtener los registros del usuario " + str(autor))
                preguntas = None
                respuestas = None
                enlaces = None
                comentarios = None
            
            # modificamos cada registro
            if preguntas:
                for p in preguntas:
                    p.puntos = puntos
            if respuestas:
                for r in respuestas:
                    r.puntos = puntos
            if enlaces:
                for e in enlaces:
                    e.puntos = puntos
            if comentarios:
                for c in comentarios:
                    c.puntos = puntos
            
            # guardamos los datos
            try:
                if preguntas:
                    db.put(preguntas)
                if respuestas:
                    db.put(respuestas)
                if enlaces:
                    db.put(enlaces)
                if comentarios:
                    db.put(comentarios)
                logging.info("Actualizado el karma del usuario " + str(autor))
            except:
                logging.error("Imposible actualizar el karma del usuario " + str(autor))
        else:
            logging.info("El elemento seleccionado pertenece a un usuario anonimo")
    
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

if __name__ == "__main__":
    karma()

