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

import logging
from google.appengine.ext import db
from base import *

class Procesar_seguimientos:
    def __init__(self):
        for s in Seguimiento.all():
            self.procesar(s)
    
    def procesar(self, s):
        p = s.get_pregunta()
        if s.respuestas < p.respuestas: # nuevas respuestas
            for u in s.usuarios:
                n = Notificacion()
                n.link = p.get_link() + '#' + str(s.respuestas)
                n.usuario = u
                n.mensaje = 'La pregunta "' + p.titulo[:99] + '" tiene ' + str(p.respuestas - s.respuestas)
                n.mensaje += ' respuestas nuevas, de un total de ' + str(p.respuestas) + '.'
                try:
                    n.put()
                    n.borrar_cache()
                except:
                    logging.warning('Imposible guardar la notificación')
            try:
                s.respuestas = p.respuestas
                s.put()
            except:
                logging.warning('Imposible actualizar pregunta: ' + str(p.key()))
        elif s.estado != p.estado: # cambio de estado
            for u in s.usuarios:
                n = Notificacion()
                n.link = p.get_link()
                n.usuario = u
                n.mensaje = 'La pregunta "' + p.titulo[:99] + '" ha sido marcada como ' + p.get_estado() + '.'
                try:
                    n.put()
                except:
                    logging.warning('Imposible guardar la notificación')
            try:
                s.estado = p.estado
                s.put()
            except:
                logging.warning('Imposible actualizar pregunta: ' + str(p.key()))

if __name__ == "__main__":
    Procesar_seguimientos()

