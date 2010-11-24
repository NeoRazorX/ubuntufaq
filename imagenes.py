#!/usr/bin/env python

import cgi, os, math, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from recaptcha.client import captcha
from datetime import datetime
from base import *

class Imagenes(Pagina):
    def get(self, pagina=0):
        Pagina.get(self)
        
        enlaces_query = db.GqlQuery("SELECT * FROM Enlace WHERE tipo_enlace = 'imagen' ORDER BY fecha DESC")
        
        # calculamos todo lo necesario para paginar
        paginas = int( math.ceil(enlaces_query.count() / 10.0) )
        if paginas < 1:
            paginas = 1
        pag_actual = 0
        if str(pagina).isdigit():
            pag_actual = int( pagina )
        
        # paginamos
        imagenes = enlaces_query.fetch(10, int(10 * pag_actual) )
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = "recaptcha-public-key",
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': 'Imagenes de Ubuntu FAQ',
            'descripcion': 'Todas las imagenes de actualidad en torno a Ubuntu Linux',
            'tags': 'ubufaq, ubuntu faq, imagenes ubuntu, wallpapers ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'imagenes',
            'imagenes': imagenes,
            'captcha': chtml,
            'paginas': paginas,
            'rango_paginas': range(paginas),
            'pag_actual': pag_actual,
            'usuario': users.get_current_user()
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/imagenes.html')
        self.response.out.write(template.render(path, template_values))

