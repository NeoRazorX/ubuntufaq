#!/usr/bin/env python

import cgi, os, logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from recaptcha.client import captcha
from datetime import datetime
from base import *

class Actualidad(Pagina):
    # muestra los ultimos enlaces
    def get(self, p=0):
        Pagina.get(self)
        
        enlaces_query = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC")
        
        # paginamos
        enlaces, paginas, p_actual = self.paginar(enlaces_query, 20, p)
        
        template_values = {
            'titulo': 'Actualidad de Ubuntu FAQ',
            'descripcion': 'Noticias, blogs, videos, imagenes y en definitiva toda la actualidad en torno a Ubuntu y Linux en general. Comparte con nosotros!',
            'tags': 'ubufaq, ubuntu faq, noticias ubuntu, actualidad ubuntu, linux, lucid, maverick, natty',
            'url': self.url,
            'url_linktext': self.url_linktext,
            'mi_perfil': self.mi_perfil,
            'formulario': self.formulario,
            'vista': 'actualidad',
            'enlaces': enlaces,
            'paginas': paginas,
            'rango_paginas': range(paginas),
            'pag_actual': p_actual,
            'usuario': users.get_current_user(),
            'error_dominio': self.error_dominio
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/actualidad.html')
        self.response.out.write(template.render(path, template_values))
    
    # crea un nuevo enlace
    def post(self):
        if self.request.get('url') and self.request.get('descripcion'):
            # comprobamos que no se haya introducido anteriormente el enlace
            url = self.request.get('url')
            enlaces = db.GqlQuery("SELECT * FROM Enlace WHERE url = :1", url).fetch(1)
            if enlaces:
                self.redirect('/story/' + str( enlaces[0].key() ))
            else:
                enl = Enlace()
                enl.descripcion = cgi.escape( self.request.get('descripcion').replace("\n", ' ') )
                enl.url = url
                enl.os = self.request.environ['HTTP_USER_AGENT']
                
                if users.get_current_user():
                    if self.request.get('anonimo') != 'on':
                        enl.autor = users.get_current_user()
                    try:
                        enl.put()
                        enl.borrar_cache()
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
                        RECAPTCHA_PRIVATE_KEY,
                        remoteip)
                    
                    if cResponse.is_valid:
                        try:
                            enl.put()
                            enl.borrar_cache()
                            self.redirect('/story/' + str( enl.key() ))
                        except:
                            logging.warning('Imposible guardar enlace a: ' + url)
                            self.redirect('/error/503')
                    else:
                        self.redirect('/error/403c')
        else:
            self.redirect('/error/403')

class Redir_enlace(webapp.RequestHandler):
    def get(self, id_enlace=None):
        if id_enlace:
            self.redirect('/story/' + id_enlace)
        else:
            self.redirect('/error/404')

class Detalle_enlace(Pagina):
    # muestra el enlace
    def get(self, id_enlace=None):
        Pagina.get(self)
        
        try:
            e = Enlace.get( id_enlace )
        except:
            e = None
        
        if e:
            e.clickar( self.request.remote_addr )
            c = e.get_comentarios( e.comentarios )
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
            
            # el captcha
            if users.get_current_user():
                chtml = ''
            else:
                chtml = captcha.displayhtml(
                    public_key = RECAPTCHA_PUBLIC_KEY,
                    use_ssl = False,
                    error = None)
            
            if self.request.get('modificar') and users.is_current_user_admin():
                modificar = True
            else:
                modificar = False
            
            descripcion = 'Discusion sobre: ' + e.descripcion + ' | enlace a ' + tipo_enlace + ', ' + str(e.comentarios) + ' comentarios.'
            
            template_values = {
                'titulo': e.descripcion + ' - Ubuntu FAQ',
                'descripcion': descripcion,
                'tags': 'ubufaq, ubuntu faq' + self.extraer_tags(e.descripcion),
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
                'modificar': modificar,
                'usuario': users.get_current_user(),
                'error_dominio': self.error_dominio
                }
            
            path = os.path.join(os.path.dirname(__file__), 'templates/enlace.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/error/404')
    
    # modifica el enlace
    def post(self):
        try:
            e = Enlace.get( self.request.get('id') )
        except:
            e = None
        
        if e and self.request.get('url') and self.request.get('descripcion') and self.request.get('tipo_enlace'):
            if users.is_current_user_admin():
                try:
                    e.url = self.request.get('url')
                    e.descripcion = cgi.escape( self.request.get('descripcion').replace("\n", ' ') )
                    if self.request.get('tipo_enlace') in ['youtube', 'vimeo', 'vhtml5', 'imagen', 'deb', 'package', 'texto']:
                        e.tipo_enlace = self.request.get('tipo_enlace')
                    else:
                        e.tipo_enlace = None
                    e.put()
                    e.borrar_cache()
                    logging.warning('Se ha modificado el enlace con id: ' + self.request.get('id'))
                    self.redirect('/story/' + str( e.key() ))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

class Acceder_enlace(webapp.RequestHandler):
    def get(self, id_enlace=None):
        try:
            e = Enlace.get( id_enlace )
        except:
            e = None
        
        if e:
            e.clickar( self.request.remote_addr )
            self.redirect( e.url )
        else:
            self.redirect('/error/404')

class Hundir_enlace(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id'):
            try:
                e = Enlace.get( self.request.get('id') )
                e.fecha = datetime.min
                e.put()
                e.borrar_cache()
                logging.warning('Se ha hundido el enlace con id: ' + self.request.get('id'))
                self.redirect('/actualidad')
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

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
                    e.borrar_cache()
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
    def post(self):
        c = Comentario()
        c.contenido = cgi.escape( self.request.get('contenido') )
        c.id_enlace = self.request.get('id_enlace')
        c.os = self.request.environ['HTTP_USER_AGENT']
        
        if users.get_current_user() and self.request.get('contenido') and self.request.get('id_enlace'):
            if self.request.get('anonimo') != 'on':
                c.autor = users.get_current_user()
            self.finalizar( c )
        elif self.request.get('contenido') and self.request.get('id_enlace'):
            challenge = self.request.get('recaptcha_challenge_field')
            response = self.request.get('recaptcha_response_field')
            remoteip = self.request.remote_addr
            cResponse = captcha.submit(
                challenge,
                response,
                RECAPTCHA_PRIVATE_KEY,
                remoteip)
            
            if cResponse.is_valid:
                self.finalizar( c )
            else:
                self.redirect('/error/403c')
        else:
            self.redirect('/error/403')
    
    def finalizar(self, comentario):
        try:
            comentario.put()
            e = Enlace.get( comentario.id_enlace )
            e.actualizar()
            e.borrar_cache()
            self.redirect('/story/' + str( e.key() ))
        except:
            self.redirect('/error/503')

class Modificar_comentario(webapp.RequestHandler):
    def post(self):
        try:
            e = Enlace.get( self.request.get('id_enlace') )
            c = Comentario.get( self.request.get('id_comentario') )
        except:
            e = c = None
        
        if e and c and self.request.get('contenido'):
            if users.is_current_user_admin():
                try:
                    c.contenido = cgi.escape( self.request.get('contenido') )
                    c.put()
                    e.borrar_cache()
                    logging.warning('Se ha modificado el comentario con id: ' + self.request.get('id_comentario'))
                    self.redirect('/story/' + self.request.get('id_enlace'))
                except:
                    self.redirect('/error/503')
            else:
                self.redirect('/error/403')
        else:
            self.redirect('/error/403')

class Borrar_comentario(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin() and self.request.get('id') and self.request.get('c'):
            try:
                c = Comentario.get( self.request.get('c') )
                c.delete()
                e = Enlace.get( id_enlace )
                e.actualizar()
                e.borrar_cache()
                logging.warning('Se ha borrado el comentario con id: ' + self.request.get('c'))
                self.redirect('/story/' + self.request.get('id'))
            except:
                self.redirect('/error/503')
        else:
            self.redirect('/error/403')

