#!/usr/bin/env python

import logging
from google.appengine.ext import db
from google.appengine.api import users, mail, urlfetch
from base import *

class emails:
    def acortar_url(self, url):
        try:
            result = urlfetch.fetch("http://is.gd/api.php?longurl=" + url)
            if result.status_code == 200:
                return result.content
            else:
                return url
        except:
            return url
    
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
        else:
            p.enviar_email = False
            p.put()
        
        # enviamos un mail a wordpress
        if WORDPRESS_PRIVATE_EMAIL != '' and not p.enviar_email:
            subject = p.titulo
            body = p.contenido[:100] + '...'
            body += ' m&aacute;s en Ubuntu FAQ: ' + self.acortar_url('http://www.ubufaq.com/question/' + str(p.key()) )
            
            try:
                mail.send_mail("contacto@ubufaq.com", WORDPRESS_PRIVATE_EMAIL, subject, body)
                logging.info('Enviado email a wordpress para la pregunta: ' + str(p.key()))
            except:
                logging.error('Error al enviar el email a wordpress para la pregunta: ' + str(p.key()))
    
    def enviar(self, p):
        subject = "Han contestado a tu pregunta en Ubuntu FAQ"
        valores = {
            't': p.titulo,
            'l': "http://www.ubufaq.com/question/" + str(p.key())
            }
        
        body = """El motivo de este mensaje es informarte que han contestado a tu pregunta: "%(t)s".\nPuedes ver la respuesta en el siguiente enlace -> %(l)s\n\nAtentamente,\nEl Cron de Ubuntu FAQ.""" % valores
        
        try:
            mail.send_mail("contacto@ubufaq.com", p.autor.email(), subject, body)
            p.enviar_email = False
            p.put()
            logging.info('Enviado email para la pregunta: ' + str(p.key()))
        except:
            logging.error('Error al enviar el email para la pregunta: ' + str(p.key()))
    
    def __init__(self):
        preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE enviar_email = True").fetch(5)
        for p in preguntas:
            self.comprobar(p)

if __name__ == "__main__":
    emails()

