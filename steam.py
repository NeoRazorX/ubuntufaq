#!/usr/bin/env python

import logging
from google.appengine.ext import db
from google.appengine.api import mail, urlfetch
from base import *

class steam:
    def comprobar_url_steam(self):
        try:
            result = urlfetch.fetch('http://store.steampowered.com/public/client/steam_client_linux')
            if result.status_code == 200:
                return True
            else:
                return False
        except:
            return False
    
    # devuelve un array con los usuario que hayan comentado el enlace
    def recolectar_usuarios(self, id_enlace):
        autores = []
        try:
            enlace = Enlace.get( id_enlace )
            comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", id_enlace)
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
                logging.warning("No se ha encontrado ningun usuario al que avisar")
        else:
            logging.warning("La url no coincide - ya no es necesario este script?")
        return autores
    
    # envia un email a los usuarios especificados
    def enviar_mails(self, usuarios):
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
            mensaje.subject = "Steam para Linux ya disponible!"
            mensaje.body = "El motivo de este mensaje es informarte que Steam para Linux ya esta disponible http://store.steampowered.com\n\nAtentamente,\nEl Cron de Ubuntu FAQ."
            try:
                mensaje.send()
                retorno = True
            except:
                logging.error('Error al enviar el email!!!')
        else:
            logging.error('Lista de usuarios vacia!!!')
        return retorno
    
    # actualizamos el enlace para no volver a avisar
    def desactivar_enlace(self, id_enlace):
        try:
            enlace = Enlace.get( id_enlace )
            enlace.url = "http://store.steampowered.com"
            enlace.put()
        except:
            logging.error("Imposible desactivar el enlace!!!")
    
    def __init__(self):
        if STEAM_ENLACE_KEY != '':
            if self.comprobar_url_steam():
                if self.enviar_mails( self.recolectar_usuarios( STEAM_ENLACE_KEY ) ):
                    self.desactivar_enlace( STEAM_ENLACE_KEY )
            else:
                logging.info('Steam para Linux todavia no esta disponible...')

if __name__ == "__main__":
    steam()

