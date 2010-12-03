#!/usr/bin/env python

import cgi, os, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from recaptcha.client import captcha
from datetime import datetime
from base import *

class Imagenes(Pagina):
    def get(self, p=0):
        Pagina.get(self)
        
        enlaces_query = db.GqlQuery("SELECT * FROM Enlace WHERE tipo_enlace = 'imagen' ORDER BY fecha DESC")
        
        # paginamos
        imagenes, paginas, p_actual = self.paginar(enlaces_query, 10, p)
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': 'Imagenes de Ubuntu FAQ',
            'descripcion': 'Wallpapers, screenshots e imagenes de actualidad en torno a Ubuntu Linux',
            'tags': 'ubufaq, ubuntu faq, imagenes ubuntu, wallpapers ubuntu, screenshots ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'imagenes',
            'imagenes': imagenes,
            'captcha': chtml,
            'paginas': paginas,
            'rango_paginas': range(paginas),
            'pag_actual': p_actual,
            'usuario': users.get_current_user()
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/imagenes.html')
        self.response.out.write(template.render(path, template_values))

