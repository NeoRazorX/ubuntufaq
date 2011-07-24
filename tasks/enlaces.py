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
from base import *

class enlaces:
    def __init__(self):
        enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE tipo_enlace = :1", None).fetch(25)
        for e in enlaces:
            self.comprobar( e )
    
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
            try:
                enlace.put()
                enlace.borrar_cache()
            except:
                logging.error('Imposible modificar el enlace!')


if __name__ == "__main__":
    enlaces()

