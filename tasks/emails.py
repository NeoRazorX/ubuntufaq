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
        query = db.GqlQuery("SELECT * FROM Usuario")
        usuarios = query.fetch(20, random.randint(0, max(0, query.count()-20)))
        for u in usuarios:
            if self.comprobar(u):
                break;
    
    def comprobar(self, u):
        retorno = False
        logging.info('Comprobando notificaciones para el usuario: ' + u.usuario.email())
        notis = db.GqlQuery("SELECT * FROM Notificacion WHERE usuario = :1 ORDER BY fecha DESC", u.usuario).fetch(20)
        if notis:
            if u.emails:
                enviar = False
                for n in notis:
                    if n.email:
                        enviar = True
                if enviar:
                    retorno = self.enviar(u, notis)
            else:
                logging.info('No quiere recibir emails')
                for n in notis:
                    try:
                        n.email = False
                        n.put()
                    except:
                        logging.warning('Imposible modificar notificación: ' + str(n.key()))
        else:
            logging.info('No tiene notificaciones')
        return retorno
    
    def enviar(self, u, notis):
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
        body += "\nAccede a tu perfil desde: http://www.ubufaq.com/u/" + urllib.quote( base64.b64encode( u.usuario.email() ) )
        body += "\n\nAtentamente,\nEl cron de Ubuntu FAQ."
        try:
            mail.send_mail("contacto@ubufaq.com", u.usuario.email(), subject, body)
            logging.info('Enviado email para el usuario: ' + u.usuario.email())
            logging.info(body)
            return True
        except:
            logging.warning('Error al enviar el email para el usuario: ' + u.usuario.email())
            return False


if __name__ == "__main__":
    emails()

