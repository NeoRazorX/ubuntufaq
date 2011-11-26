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
from datetime import datetime, timedelta
from base import *

class antiguas:
    sc = Super_cache()
    
    def __init__(self):
        self.marcar_preguntas()
        self.borrar_enlaces()
    
    def marcar_preguntas(self):
        preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE fecha < :1 ORDER BY fecha ASC LIMIT 50",
                                datetime.today() - timedelta(days= 90))
        for p in preguntas:
            if p.estado not in[14, 13, 12, 10, 3]:
                p.estado = 14
                try:
                    p.put()
                    p.borrar_cache()
                    logging.info('Marcada como antigua la pregunta: ' + p.get_link())
                    self.sc.borrar_cache_pregunta( str(p.key()) )
                except:
                    logging.warning('Imposible marcar como antigua la pregunta: ' + p.get_link())
    
    def borrar_enlaces(self):
        enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE fecha < :1 ORDER BY fecha ASC LIMIT 50",
                                datetime.today() - timedelta(days= 90))
        for e in enlaces:
            if e.comentarios == 0:
                try:
                    e.borrar_todo()
                    logging.info('Borrado en enlace: ' + e.get_link() + ' por antiguo.')
                    self.sc.borrar_cache_enlace( str(p.key()) )
                except:
                    logging.warning('Imposible borrar el enlace: ' + e.get_link() + ' por antiguo.')

if __name__ == "__main__":
    antiguas()

