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

import logging, random, urllib, base64
from google.appengine.ext import db
from google.appengine.api import users, mail
from base import *

class emails:
    def __init__(self):
        notis = db.GqlQuery("SELECT * FROM Notificacion WHERE email = :1", True).fetch(20)
        pendientes = {}
        for n in notis:
            if n.usuario.email() not in pendientes:
                pendientes[n.usuario.email()] = [n]
            else:
                pendientes[n.usuario.email()].append(n)
        for email in pendientes.keys():
            self.enviar(email, pendientes[email])
    
    def enviar(self, email, notis):
        subject = "Notificación de Ubuntu FAQ"
        body = ''
        for n in notis:
            if n.email:
                try:
                    body += '- ' + n.mensaje + "\n"
                    n.email = False
                    n.put()
                except:
                    logging.warning('Imposible modificar notificación: ' + str(n.key()))
        body += "\nAccede a tu perfil desde: http://www.ubufaq.com/u/" + urllib.quote( base64.b64encode( email ) )
        body += "\n\nAtentamente,\nEl cron de Ubuntu FAQ."
        try:
            mail.send_mail("contacto@ubufaq.com", email, subject, body)
            logging.info('Enviado email para el usuario: ' + email)
            logging.info(body)
            return True
        except:
            logging.warning('Error al enviar el email para el usuario: ' + email())
            return False

if __name__ == "__main__":
    emails()
