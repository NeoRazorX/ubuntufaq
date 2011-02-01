#!/usr/bin/env python

import logging
from google.appengine.ext import db
from google.appengine.api import mail, urlfetch, users, memcache
from datetime import datetime
from base import *

class steam:
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
        try:
            enlace = Enlace.get( STEAM_ENLACE_KEY )
            comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", STEAM_ENLACE_KEY)
        except:
            enlace = comentarios = None
        
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
            enlace = Enlace.get( STEAM_ENLACE_KEY )
            enlace.url = "http://store.steampowered.com"
            enlace.put()
        except:
            logging.error("Unable to disable link!!!")
    
    def clean_garbage(self):
        comments = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha DESC", STEAM_ENLACE_KEY).fetch(100)
        code = ''
        for co in comments:
            if co.os == 'steam.py' and co.contenido == code:
                co.delete()
            elif co.os == 'steam.py':
                code = co.contenido
    
    def make_a_comment(self, comment):
        c = Comentario()
        c.contenido = comment
        c.id_enlace = STEAM_ENLACE_KEY
        c.os = 'steam.py'
        
        e = Enlace.get( STEAM_ENLACE_KEY )
        e.comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1", STEAM_ENLACE_KEY).count()
        e.fecha = datetime.now()
        
        try:
            c.put()
            e.put()
            memcache.delete( STEAM_ENLACE_KEY )
            memcache.delete('steam4linux')
        except:
            logging.error('Cant save comment: ' + comment)
    
    def __init__(self):
        if STEAM_ENLACE_KEY != '':
            code = self.check_steam_url()
            if code == 200:
                if self.send_emails( self.collect_users() ):
                    self.disable_link()
                    self.make_a_comment('STEAM FOR LINUX READY!!!')
            else:
                logging.info('Steam for Linux not ready yet...')
                self.clean_garbage()
                self.make_a_comment('Steam for Linux not ready yet... code: ' + str(code))
        else:
            logging.info('STEAM_ENLACE_KEY is empty!')

if __name__ == "__main__":
    steam()

