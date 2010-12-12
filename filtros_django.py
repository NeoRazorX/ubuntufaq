#!/usr/bin/env python

import hashlib, random, urllib
from google.appengine.ext import webapp
from datetime import datetime


register = webapp.template.create_template_register()


def cortamail(email):
    return str(email).split('@')[0]


def menu_cabecera(vista, seleccion=''):
    if vista == seleccion:
        return 'id="menusel"'
    else:
        return ''


def avatar(email, size=80):
    if email:
        return '<img src="http://www.gravatar.com/avatar/' + hashlib.md5(str(email)).hexdigest() + '?s=' + str(size) + '" alt="avatar" />'
    elif size == 40:
        return '<img src="/img/anonymous-40.gif" alt="anonymous" />'
    else:
        return '<img src="/img/anonymous.gif" alt="anonymous" />'


def karmsg(puntos):
    if puntos > 1:
        return '&iexcl;Ha salvado a ' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    else:
        return 'Usuario poco participativo...'


def puntos(puntos):
    if puntos > 1:
        return '<a href="/ayuda#karma">' + str(puntos) + '</a>'
    else:
        return ''


def estado_pregunta(estado):
    retorno = 'estado desconocido'
    
    if estado == 0:
        retorno = 'nueva'
    elif estado == 1:
        retorno = 'incompleta'
    elif estado == 2:
        retorno = 'abierta'
    elif estado == 3:
        retorno = 'parcialmente solucionada'
    elif estado == 10:
        retorno = 'solucionada'
    elif estado == 11:
        retorno = 'pendiente de confirmaci&oacute;n'
    elif estado == 12:
        retorno = 'duplicada'
    elif estado == 13:
        retorno = 'erronea'
    
    return retorno


def randomsg(enlaces):
    eleccion = random.randint(0, 11)
    
    if eleccion == 0:
        enlace = '/actualidad#nuevo-enlace'
        imagen = '/img/tux-want-you.png'
        mensaje = 'Tux dice que compartas con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    elif eleccion == 1:
        enlace = '/actualidad#nuevo-enlace'
        imagen = '/img/ubufuck.png'
        mensaje = 'Comparte con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    elif eleccion == 2:
        enlace = '/actualidad#nuevo-enlace'
        imagen = '/img/ubufuck2.png'
        mensaje = 'Comparte con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    elif eleccion == 3:
        enlace = 'http://www.ubufaq.com'
        imagen = '/img/ubufaq.png'
        mensaje = 'Recuerda la direcci&oacute;n: ubufaq.com'
    elif eleccion == 4:
        enlace = 'http://www.ubufaq.com'
        imagen = '/img/ubufaq2.png'
        mensaje = 'Recuerda la direcci&oacute;n: ubufaq.com'
    elif eleccion == 5:
        enlace = '/actualidad#nuevo-enlace'
        imagen = '/img/traje-anonymous.png'
        mensaje = 'Anonymous tambi&eacute;n comparte enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    else:
        enlace = '/images'
        mensaje = 'Nueva galer&iacute;a de im&aacute;genes (beta)'
        imagen = ''
        for enl in enlaces:
            if enl.tipo_enlace == 'imagen' and imagen == '' and random.randint(0, 2) == 0:
                imagen = 'http://api.thumbalizr.com/?url=' + urllib.quote( str(enl.url) )
        if imagen == '':
            imagen = '/img/ubufuck2.png'
    
    return '<a href="' + enlace + '"><img src="' + imagen + '" alt="' + imagen + '" title="' + mensaje + '"/></a>'


register.filter( cortamail )
register.filter( menu_cabecera )
register.filter( avatar )
register.filter( karmsg )
register.filter( puntos )
register.filter( estado_pregunta )
register.filter( randomsg )

