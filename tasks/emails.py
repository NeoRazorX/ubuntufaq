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

import logging
from google.appengine.ext import db
from google.appengine.api import users, mail
from base import *

class emails:
    def __init__(self):
        preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE enviar_email = True").fetch(5)
        for p in preguntas:
            self.comprobar(p)
    
    def comprobar(self, p):
        if p.autor:
            respuestas = db.GqlQuery("SELECT * FROM Respuesta WHERE id_pregunta = :1", str( p.key() )).fetch(10)
            if len(respuestas) == 1:
                if respuestas[0].autor != p.autor:
                    self.enviar(p)
            elif len(respuestas) > 1:
                for r in respuestas:
                    if r.autor != p.autor:
                        self.enviar(p)
                        break
        else: # es una pregunta anonima
            p.enviar_email = False
            p.stop_emails = True
            p.put()
    
    def enviar(self, p):
        subject = "Han contestado a tu pregunta en Ubuntu FAQ"
        valores = {
            't': p.titulo,
            'l': "http://www.ubufaq.com/question/" + str(p.key()),
            'l2': "http://www.ubufaq.com/stop_emails/" + str(p.key())
            }
        
        body = """El motivo de este mensaje es informarte que han contestado a tu pregunta: "%(t)s".\nPuedes ver la respuesta en el siguiente enlace -> %(l)s\nSi no deseas recivir mas mensajes, haz clic en el siguiente enlace -> %(l2)s\n\nAtentamente,\nEl Cron de Ubuntu FAQ.""" % valores
        
        try:
            mail.send_mail("contacto@ubufaq.com", p.autor.email(), subject, body)
            p.enviar_email = False
            p.put()
            logging.info('Enviado email para la pregunta: ' + str(p.key()))
        except:
            logging.error('Error al enviar el email para la pregunta: ' + str(p.key()))


if __name__ == "__main__":
    emails()

