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

# cargamos django 1.2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from base import *

class Stop_emails(webapp.RequestHandler):
    def get(self):
        try:
            query = db.GqlQuery("SELECT * FROM Usuario WHERE usuario = :1", users.get_current_user()).fetch(1)
            if query:
                u = query[0]
            else:
                u = Usuario()
                u.usuario = users.get_current_user()
            u.emails = not u.emails
            u.put()
            self.redirect('/u/' + urllib.quote( base64.b64encode( users.get_current_user().email() ) ) )
        except:
            self.redirect('/error/503')

def main():
    application = webapp.WSGIApplication( [('/stop_emails', Stop_emails)], debug=DEBUG_FLAG )
    template.register_template_library('filters.filtros_django')
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
