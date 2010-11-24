#!/usr/bin/env python

import logging
from google.appengine.ext import db
from base import *

class enlaces:
    def comprobar(self, enlace):
        tipo_enlace = 'texto'
        
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
            enlace.put()
    
    def __init__(self):
        enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE tipo_enlace = :1", None).fetch(25)
        for e in enlaces:
            self.comprobar( e )

if __name__ == "__main__":
    enlaces()

