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
from google.appengine.api import mail, urlfetch, users, memcache
from datetime import datetime
from base import *

class steam:
    sc = Super_cache()
    
    # returns the status code of the http request
    def check_steam_url(self):
        try:
            result = urlfetch.fetch('http://store.steampowered.com/public/client/steam_client_linux')
            return result.status_code
        except:
            return 404
    
    # return an array with all unique non-anonymous users
    # only if link is active -> enlace.url != 'http://store.steampowered.com'
    def collect_users(self):
        autores = []
        enlace = self.sc.get_enlace( STEAM_ENLACE_KEY )
        comentarios = self.sc.get_comentarios_de( STEAM_ENLACE_KEY )
        if enlace.url != 'http://store.steampowered.com':
            if comentarios.count() > 0:
                # seleccionamos los autores
                autores = []
                for usu1 in comentarios:
                    if usu1.autor == None:
                        pass
                    elif usu1.autor not in autores:
                        autores.append( usu1.autor )
            else:
                logging.warning("Empty user list!")
        else:
            logging.warning("URL do not match!")
        return autores
    
    # send an email to everyone in the usuarios array
    def send_emails(self, usuarios):
        retorno = False
        if len( usuarios ) > 0:
            mensaje = mail.EmailMessage()
            mensaje.sender = "contacto@ubufaq.com"
            lista = ''
            for usu in usuarios:
                if lista == '':
                    lista += usu.email()
                else:
                    lista += ', ' + usu.email()
            mensaje.bcc = lista
            mensaje.subject = "Steam for Linux ready!!!"
            mensaje.body = "Yoy can check Steam for Linux now: http://store.steampowered.com http://www.ubufaq.com/steam4linux\n\nWith love,\nUbuntu FAQ's cron."
            try:
                mensaje.send()
                retorno = True
            except:
                logging.error('Cant send email!!!')
        else:
            logging.error('Empty user list!!!')
        return retorno
    
    # disable link so collect_users returns an empty array
    def disable_link(self):
        try:
            enlace = self.sc.get_enlace( STEAM_ENLACE_KEY )
            if enlace:
                enlace.url = "http://store.steampowered.com"
                enlace.put()
                self.sc.borrar_cache_enlace( STEAM_ENLACE_KEY )
        except:
            logging.error("Unable to disable link!!!")
    
    def __init__(self):
        if STEAM_ENLACE_KEY != '':
            code = self.check_steam_url()
            if code == 200:
                if self.send_emails( self.collect_users() ):
                    self.disable_link()
            else:
                logging.info('Steam for Linux not ready yet. Code: ' + str(code))
        else:
            logging.info('STEAM_ENLACE_KEY is empty!')

if __name__ == "__main__":
    steam()
