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

import os, logging, cgi, urllib, base64

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from base import *

class Redir_notificacion(webapp.RequestHandler):
    def get(self, keyn=None):
        try:
            n = Notificacion.get( keyn )
            n.delete()
            n.borrar_cache()
            self.redirect( n.link )
        except:
            self.redirect('/error/503')
    
    def post(self, keyn=None):
        if self.request.get('destinatario') and self.request.get('texto'):
            try:
                n = Notificacion()
                n.usuario = users.User( self.request.get('destinatario') )
                n.link = '/u/' + urllib.quote( base64.b64encode( users.get_current_user().email() ) )
                n.mensaje = users.get_current_user().nickname() + ' te dice: ' + cgi.escape( self.request.get('texto')[:450].replace("\n", ' ') )
                n.put()
                n.borrar_cache()
                self.redirect('/u/' + urllib.quote( base64.b64encode( self.request.get('destinatario') ) ) + '?priv=True')
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

def main():
    application = webapp.WSGIApplication( [(r'/noti/(.*)', Redir_notificacion)], debug=DEBUG_FLAG )
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
