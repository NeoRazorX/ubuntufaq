#!/usr/bin/env python

import cgi, os, math, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from recaptcha.client import captcha
from datetime import datetime
from base import *

class Enlazar(webapp.RequestHandler):
    def post(self):
        if self.request.get('url') and self.request.get('descripcion'):
            # comprobamos que no se haya introducido anteriormente el enlace
            url = cgi.escape( self.request.get('url') )
            enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE url = :1", url).fetch(1)
            if enlaces:
                self.redirect('/story/' + str( enlaces[0].key() ))
            else:
                enl = Enlace()
                enl.descripcion = cgi.escape( self.request.get('descripcion').replace("\n", ' ') )
                
                if users.get_current_user():
                    try:
                        enl.autor = users.get_current_user()
                        enl.url = url
                        enl.put()
                        self.redirect('/story/' + str( enl.key() ))
                    except:
                        logging.warning('Imposible guardar enlace a: ' + url)
                        self.redirect('/error/503')
                else:
                    challenge = self.request.get('recaptcha_challenge_field')
                    response  = self.request.get('recaptcha_response_field')
                    remoteip  = self.request.remote_addr
                    cResponse = captcha.submit(
                        challenge,
                        response,
                        "recaptcha-private-key",
                        remoteip)
                    
                    if cResponse.is_valid:
                        try:
                            enl.url = url
                            enl.put()
                            self.redirect('/story/' + str( enl.key() ))
                        except:
                            logging.warning('Imposible guardar enlace a: ' + url)
                            self.redirect('/error/503')
                    else:
                        self.redirect('/error/403c')
        else:
            self.redirect('/error/403')

class Actualidad(Pagina):
    def get(self, pagina=0):
        Pagina.get(self)
        
        enlaces_query = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC")
        
        # calculamos todo lo necesario para paginar
        paginas = int( math.ceil(enlaces_query.count() / 20.0) )
        if paginas < 1:
            paginas = 1
        pag_actual = 0
        if str(pagina).isdigit():
            pag_actual = int( pagina )
        
        # paginamos
        enlaces = enlaces_query.fetch(20, int(20 * pag_actual) )
        
        # el captcha
        if users.get_current_user():
            chtml = ''
        else:
            chtml = captcha.displayhtml(
                public_key = "recaptcha-public-key",
                use_ssl = False,
                error = None)
        
        template_values = {
            'titulo': 'Actualidad de Ubuntu FAQ',
            'descripcion': 'Toda la actualidad en torno a Ubuntu Linux',
            'tags': 'ubufaq, ubuntu faq, noticias ubuntu, actualidad ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'actualidad',
            'enlaces': enlaces,
            'captcha': chtml,
            'paginas': paginas,
            'rango_paginas': range(paginas),
            'pag_actual': pag_actual,
            'usuario': users.get_current_user()
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/actualidad.html')
        self.response.out.write(template.render(path, template_values))

class Detalle_enlace(Pagina):
    def get(self, id_enlace=None):
        Pagina.get(self)
        
        try:
            e = Enlace.get( id_enlace )
        except:
            e = None
        
        if e:
            # actualizamos los clicks, no pasa nada si no podemos
            if e.ultima_ip != self.request.remote_addr:
                e.ultima_ip = self.request.remote_addr
                e.clicks += 1
                try:
                    e.put()
                except:
                    pass
            
            tipo_enlace = 'texto'
            aux_enlace = None
            
            if e.url[:23] == 'http://www.youtube.com/':
                tipo_enlace = 'youtube'
                aux_enlace = e.url.split('?v=')[1]
            elif e.url[:21] == 'http://www.vimeo.com/':
                tipo_enlace = 'vimeo'
                aux_enlace = e.url.split('/')[3]
            elif e.url[-4:] in ['.ogv', '.OGV', '.mp4', '.MP4'] or e.url[-5:] in ['.webm', '.WEBM']:
                tipo_enlace = 'vhtml5'
            elif e.url[-4:] in ['.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF'] or e.url[-5:] in ['.jpeg', '.JPEG']:
                tipo_enlace = 'imagen'
            elif e.url[-4:] in ['.deb', '.DEB']:
                tipo_enlace = 'deb'
            elif e.url[-4:] in ['.deb', '.DEB', '.tgz', '.TGZ', '.bz2', '.BZ2'] or e.url[-3:] in ['.gz', '.GZ']:
                tipo_enlace = 'package'
            
            # obtenemos los comentarios
            c = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1 ORDER BY fecha ASC", str( e.key() )).fetch(100)
            
            # el captcha
            if users.get_current_user():
                chtml = ''
            else:
                chtml = captcha.displayhtml(
                    public_key = "recaptcha-public-key",
                    use_ssl = False,
                    error = None)
            
            template_values = {
                'titulo': 'UbuntuFAQ - ' + e.descripcion,
                'descripcion': 'Discusion sobre: ' + e.descripcion,
                'tags': 'ubufaq, ubuntu faq, noticias ubuntu, actualidad ubuntu, linux, lucid, maverick, natty',
                'url': self.url,
                'url_linktext': self.url_linktext,
                'mi_perfil': self.mi_perfil,
                'formulario': self.formulario,
                'enlace': e,
                'tipo_enlace': tipo_enlace,
                'aux_enlace': aux_enlace,
                'comentarios': c,
                'captcha': chtml,
                'administrador': users.is_current_user_admin(),
                'usuario': users.get_current_user()
                }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/enlace.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')

class Redir_enlace(webapp.RequestHandler):
    def get(self, id_enlace=None):
        try:
            e = Enlace.get( id_enlace )
        except:
            e = None
        
        if e:
            # actualizamos los clicks, no pasa nada si no podemos
            if e.ultima_ip != self.request.remote_addr:
                e.ultima_ip = self.request.remote_addr
                e.clicks += 1
                try:
                    e.put()
                except:
                    pass
            self.redirect( e.url )
        else:
            self.redirect('/error/404')

class Borrar_enlace(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id'):
            continuar = True
            try:
                c = Comentario.all().filter('id_enlace =', self.request.get('id'))
                db.delete(c)
            except:
                continuar = False
            
            if continuar:
                try:
                    e = Enlace.get( self.request.get('id') )
                    e.delete()
                    logging.warning('Se ha borrado el enlace con id: ' + self.request.get('id'))
                    self.redirect('/actualidad')
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

class Comentar(webapp.RequestHandler):
    def actualizar_enlace(self, id_enlace):
        e = Enlace.get( id_enlace )
        e.comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1", id_enlace).count()
        e.fecha = datetime.now()
        e.put()
    
    def post(self):
        c = Comentario()
        c.contenido = cgi.escape( self.request.get('contenido') )
        c.id_enlace = self.request.get('id_enlace')
        
        if users.get_current_user() and self.request.get('contenido') and self.request.get('id_enlace'):
            c.autor = users.get_current_user()
            try:
                c.put()
                self.actualizar_enlace( self.request.get('id_enlace') )
                self.redirect('/story/' + self.request.get('id_enlace'))
            except:
                self.redirect('/error/503')
        elif self.request.get('contenido') and self.request.get('id_enlace'):
            challenge = self.request.get('recaptcha_challenge_field')
            response = self.request.get('recaptcha_response_field')
            remoteip = self.request.remote_addr
            cResponse = captcha.submit(
                challenge,
                response,
                "recaptcha-private-key",
                remoteip)
            
            if cResponse.is_valid:
                try:
                    c.put()
                    self.actualizar_enlace( self.request.get('id_enlace') )
                    self.redirect('/story/' + self.request.get('id_enlace'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403c')
        else:
            self.redirect('/error/403')

class Borrar_comentario(webapp.RequestHandler):
    def actualizar_enlace(self, id_enlace):
        e = Enlace.get( id_enlace )
        e.comentarios = db.GqlQuery("SELECT * FROM Comentario WHERE id_enlace = :1", id_enlace).count()
        e.put()
    
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('c'):
            try:
                c = Comentario.get( self.request.get('c') )
                c.delete()
                self.actualizar_enlace( self.request.get('id') )
                logging.warning('Se ha borrado el comentario con id: ' + self.request.get('c'))
                self.redirect('/story/' + self.request.get('id'))
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

