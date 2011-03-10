#!/usr/bin/env python

import logging
from google.appengine.ext import db
from google.appengine.api import mail, urlfetch
from base import *

class enlaces:
    def acortar_url(self, url):
        try:
            result = urlfetch.fetch("http://is.gd/api.php?longurl=" + url)
            if result.status_code == 200:
                return result.content
            else:
                return url
        except:
            return url
    
    def comprobar(self, enlace):
        tipo_enlace = 'texto'
        url_corta = self.acortar_url('http://www.ubufaq.com/e/' + str(enlace.key()) )
        # no asignar la url_corta a enlace.url, porque esto hace que el script rss-scanner publique duplicados
        
        if enlace.url[:23] == 'http://www.youtube.com/':
            tipo_enlace = 'youtube'
        elif enlace.url[:21] == 'http://www.vimeo.com/':
            tipo_enlace = 'vimeo'
        elif enlace.url[-4:] in ['.ogv', '.OGV', '.mp4', '.MP4'] or enlace.url[-5:] in ['.webm', '.WEBM']:
            tipo_enlace = 'vhtml5'
        elif enlace.url[-4:] in ['.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF'] or enlace.url[-5:] in ['.jpeg', '.JPEG']:
            tipo_enlace = 'imagen'
        elif enlace.url[-4:] in ['.deb', '.DEB']:
            tipo_enlace = 'deb'
        elif enlace.url[-4:] in ['.deb', '.DEB', '.tgz', '.TGZ', '.bz2', '.BZ2'] or enlace.url[-3:] in ['.gz', '.GZ']:
            tipo_enlace = 'package'
        
        if enlace.tipo_enlace != tipo_enlace:
            enlace.tipo_enlace = tipo_enlace
            try:
                enlace.put()
                enlace.borrar_cache()
            except:
                logging.error('Imposible modificar el enlace!')
        
        # enviamos un mail a wordpress
        if WORDPRESS_PRIVATE_EMAIL != '' and enlace.os != 'rss-scanner.py':
            if len(enlace.descripcion) < 50:
                subject = body = enlace.descripcion
            else:
                subject = enlace.descripcion[:50] + '...'
                body = enlace.descripcion
            
            if tipo_enlace == 'texto':
                body += ' - Fuente: ' + url_corta
                body += ' m&aacute;s en Ubuntu FAQ: ' + self.acortar_url('http://www.ubufaq.com/story/' + str(enlace.key()) )
            else:
                body += ' - ' + self.acortar_url('http://www.ubufaq.com/story/' + str(enlace.key()) )
            
            try:
                mail.send_mail("contacto@ubufaq.com", WORDPRESS_PRIVATE_EMAIL, subject, body)
            except:
                logging.error('Error al enviar el email a wordpress para el enlace: ' + str(enlace.key()))
    
    def __init__(self):
        enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE tipo_enlace = :1", None).fetch(25)
        for e in enlaces:
            self.comprobar( e )

if __name__ == "__main__":
    enlaces()

