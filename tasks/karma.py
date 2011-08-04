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
        # elegimos aleatoriamente una tabla para ir añadiendo usuarios a la lista
        for i in range(3):
            if self.seleccionar( random.randint(0, 3) ):
                break;
        # si aun así no se encuentran usuarios...
        if len( self.pending_users ) < 1:
            self.seleccionar(4)
        # elegimos y procesamos aleatoriamente  de uno a tres usuarios
        if len( self.pending_users ) > 1:
            for i in range(3):
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
    
    # a partir de una tabla seleccionada se buscan usuarios para añadir a la lista
    def seleccionar(self, tabla):
        retorno = True
        if tabla == 0:
            seleccion = db.GqlQuery("SELECT * FROM Enlace WHERE puntos = 0").fetch(20)
        elif tabla == 1:
            seleccion = db.GqlQuery("SELECT * FROM Comentario WHERE puntos = 0").fetch(20)
        elif tabla == 2:
            seleccion = db.GqlQuery("SELECT * FROM Pregunta WHERE puntos = 0").fetch(20)
        elif tabla == 3:
            seleccion = db.GqlQuery("SELECT * FROM Respuesta WHERE puntos = 0").fetch(20)
        else:
            logging.warning('Buscando en todas las respuestas...')
            query = db.GqlQuery("SELECT * FROM Respuesta")
            if query.count() > 0:
                seleccion = query.fetch(20, random.randint(0, max(0, query.count()-1)))
            else:
                seleccion = []
        if len( seleccion ) > 0:
            # marcamos los anonimos y seleccionamos los usuarios
            for usu1 in seleccion:
                if usu1.autor == None:
                    usu1.puntos = -1
                    usu1.put()
                elif usu1.autor not in self.pending_users:
                    self.pending_users.append( usu1.autor )
        else:
            retorno = False
        return retorno
    
    # calculamos el karma de un usuario y actualizamos los datos una vez calculado
    def calcular(self, autor):
        if autor:
            # leemos los datos del usuario
            continuar = True
            query = db.GqlQuery("SELECT * FROM Usuario WHERE usuario = :1", autor).fetch(1)
            if query:
                karma = query[0]
            else:
                karma = Usuario()
                karma.usuario = autor
            
            if karma.iterador == 0 and continuar:
                query = db.GqlQuery("SELECT * FROM Pregunta WHERE autor = :1", autor)
                karma.preguntas = query.count()
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las preguntas')
                continuar = False
            
            if karma.iterador == 1 and continuar:
                query = db.GqlQuery("SELECT * FROM Respuesta WHERE autor = :1", autor)
                karma.respuestas = query.count()
                # lo ideal es responder más que preguntas
                try:
                    karma.puntos = max(0.0, min(10.0, (2 * float(karma.respuestas) / karma.preguntas )))
                except:
                    karma.puntos = max(0.0, min(10.0, ( karma.preguntas*0.25 + karma.respuestas*0.5 )))
                # +0.5 si tiene más de 100 respuestas
                if karma.respuestas > 100:
                    karma.puntos += 0.5
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las respuestas')
                logging.info("Karma: " + str(karma.puntos))
                continuar = False
            
            if karma.iterador == 2 and continuar:
                query = db.GqlQuery("SELECT * FROM Enlace WHERE autor = :1", autor)
                karma.enlaces = query.count()
                # cuantos más enlaces mejor
                try:
                    karma.puntos += max(0, min(4, (0.4 * karma.enlaces) ))
                except:
                    pass
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a los enlaces')
                logging.info("Karma: " + str(karma.puntos))
                continuar = False
            
            if karma.iterador == 3 and continuar:
                query = db.GqlQuery("SELECT * FROM Comentario WHERE autor = :1", autor)
                karma.comentarios = query.count()
                # lo ideal es tener más comentarios que enlaces
                try:
                    karma.puntos += max(0, min(3, ( float(karma.comentarios) / karma.enlaces )))
                except:
                    pass
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a los comentarios')
                logging.info("Karma: " + str(karma.puntos))
                continuar = False
            
            if karma.iterador == 4 and continuar:
                portada = memcache.get('portada')
                if portada is None:
                    logging.info('Portada no encontrada')
                    karma.puntos += 0.5
                else:
                    encontrado = False
                    for p in portada:
                        if p['autor'] == autor:
                            encontrado = True
                    # +1 por estar en portada
                    if encontrado:
                        karma.puntos += 1
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a la portada')
                logging.info("Karma: " + str(karma.puntos))
                continuar = False
            
            if karma.iterador == 5 and continuar:
                resp = memcache.get('ultimas-respuestas')
                if resp is None:
                    logging.info('Ultimas respuestas no encontradas')
                    karma.puntos += 0.5
                else:
                    encontrado = False
                    for r in resp:
                        if r.autor == autor:
                            encontrado = True
                    # +1 por estar en las últimas respuestas
                    if encontrado:
                        karma.puntos += 1
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a las ultimas respuestas')
                logging.info("Karma: " + str(karma.puntos))
                continuar = False
            
            if karma.iterador == 6 and continuar:
                populares = memcache.get('populares')
                if populares is None:
                    logging.info('Populares no encontradas')
                    karma.puntos += 0.5
                else:
                    encontrado = False
                    for p in populares:
                        if p['autor'] == autor:
                            encontrado = True
                    # +1 por estar en populares
                    if encontrado:
                        karma.puntos += 1
                karma.iterador += 1
                logging.info("Actualizado el karma del usuario " + str(autor) + ' en base a populares')
                logging.info("Karma: " + str(karma.puntos))
                continuar = False
            
            # una vez calculado el karma pasamos a actualizar los datos
            if karma.iterador >= 14:
                karma.iterador = 0
            elif continuar and karma.iterador >= 7 and karma.iterador < 14:
                self.actualizar(autor, int(karma.puntos))
                karma.iterador += 1
            karma.put()
        else:
            logging.info("El elemento seleccionado pertenece a un usuario anonimo")
    
    # actualiza los datos de karma de un usuario
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
                logging.info("Actualizado el karma del usuario " + str(autor))
            else:
                logging.info("No hay registros para actualizar (tabla: " + str(eleccion) + ")")
        except:
            logging.warning("Imposible actualizar el karma del usuario " + str(autor))

if __name__ == "__main__":
    karma()

