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
from google.appengine.api import users, memcache
from base import *

class karma:
    def __init__(self):
        self.pending_users = memcache.get('pending-users')
        if self.pending_users is None:
            self.pending_users_memcache = False
            self.pending_users = []
        else:
            self.pending_users_memcache = True
        # elegimos aleatoriamente una tabla
        for i in range(3):
            if self.seleccionar( random.randint(0, 3) ):
                break;
        # elegimos aleatoriamente un autor
        if len( self.pending_users ) > 1:
            self.calcular( random.choice(self.pending_users) )
        elif len( self.pending_users ) == 1:
            self.calcular( self.pending_users[0] )
        else:
            logging.info("No se ha encontrado ningun usuario al que actualizar el karma")
        # guardamos o actualizamos la lista de usuarios:
        if self.pending_users_memcache:
            memcache.replace('pending-users', self.pending_users)
        else:
            memcache.add('pending-users', self.pending_users)
    
    def seleccionar(self, tabla):
        retorno = True
        if tabla == 0:
            seleccion = db.GqlQuery("SELECT * FROM Enlace WHERE puntos = 0").fetch(20)
        elif tabla == 1:
            seleccion = db.GqlQuery("SELECT * FROM Comentario WHERE puntos = 0").fetch(20)
        elif tabla == 2:
            seleccion = db.GqlQuery("SELECT * FROM Pregunta WHERE puntos = 0").fetch(20)
        else:
            seleccion = db.GqlQuery("SELECT * FROM Respuesta WHERE puntos = 0").fetch(20)
        if len( seleccion ) > 0:
            # marcamos los anonimos y seleccionamos los autores
            for usu1 in seleccion:
                if usu1.autor == None:
                    usu1.puntos = -1
                    usu1.put()
                elif usu1.autor not in self.pending_users:
                    self.pending_users.append( usu1.autor )
        else:
            retorno = False
        return retorno
    
    def calcular(self, autor):
        if autor:
            # leemos de memcache
            continuar = True
            karma = memcache.get( 'usuario_' + str(autor) )
            if karma is None:
                karma = {'puntos': 0,
                    'preguntas': False,
                    'respuestas': False,
                    'enlaces': False,
                    'comentarios': False
                }
                if memcache.add( 'usuario_' + str(autor), karma):
                    logging.info("Almacenado el karma del usuario " + str(autor) + ' en memcache')
                else:
                    logging.error("Imposible almacenar el karma del usuario " + str(autor) + ' en memcache')
                    continuar = False
            else:
                logging.info("Lellendo karma del usuario " + str(autor) + ' desde memcache')
            
            if not karma['preguntas'] and continuar:
                query = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1", autor)
                karma['puntos'] += query.count()
                karma['preguntas'] = True
                memcache.replace( 'usuario_' + str(autor), karma)
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las preguntas')
                continuar = False
            
            if not karma['respuestas'] and continuar:
                query = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1", autor)
                karma['puntos'] += (2 * query.count())
                karma['respuestas'] = True
                memcache.replace( 'usuario_' + str(autor), karma)
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las respuestas')
                continuar = False
            
            if not karma['enlaces'] and continuar:
                query = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1", autor)
                karma['puntos'] += (2 * query.count())
                karma['enlaces'] = True
                memcache.replace( 'usuario_' + str(autor), karma)
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a los enlaces')
                continuar = False
            
            if not karma['comentarios'] and continuar:
                query = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1", autor)
                karma['puntos'] += query.count()
                karma['comentarios'] = True
                memcache.replace( 'usuario_' + str(autor), karma)
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

