#!/usr/bin/env python

import hashlib, random
from google.appengine.ext import webapp
from datetime import datetime


register = webapp.template.create_template_register()


def cortamail(email):
    return str(email).split('@')[0]


def avatar(email, size=80):
    if email:
        gravatar = '<img src="http://www.gravatar.com/avatar/' + hashlib.md5(str(email)).hexdigest() + '?s=' + str(size) + '" alt="avatar" />'
    elif size == 40:
        gravatar = '<img src="/img/anonymous-40.gif" alt="anonymous" />'
    else:
        gravatar = '<img src="/img/anonymous.gif" alt="anonymous" />'
    return gravatar

def karmsg(puntos):
    mensaje = 'usuario poco participativo...'
    
    if puntos > 1:
        mensaje = '&iexcl;Ha salvado a ' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    
    return mensaje


def puntos(puntos):
    mensaje = ''
    if puntos > 1:
        mensaje = '<a href="/ayuda#karma">' + str(puntos) + '</a>'
    return mensaje


def estado_pregunta(estado):
    retorno = 'estado desconocido'
    
    if estado == 0:
        retorno = 'nueva'
    elif estado == 1:
        retorno = 'incompleta'
    elif estado == 2:
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


def randomsg(numero):
    eleccion = random.randint(0, 6)
    
    if eleccion == 0:
        enlace = '/actualidad#nuevo-enlace'
        imagen = 'tux-want-you'
        mensaje = 'Tux dice que compartas con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    elif eleccion == 1:
        enlace = '/actualidad#nuevo-enlace'
        imagen = 'ubufuck'
        mensaje = 'Comparte con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    elif eleccion == 2:
        enlace = '/actualidad#nuevo-enlace'
        imagen = 'ubufuck2'
        mensaje = 'Comparte con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    elif eleccion == 3:
        enlace = 'http://www.ubufaq.com'
        imagen = 'ubufaq'
        mensaje = 'Recuerda la direcci&oacute;n: ubufaq.com'
    elif eleccion == 4:
        enlace = 'http://www.ubufaq.com'
        imagen = 'ubufaq2'
        mensaje = 'Recuerda la direcci&oacute;n: ubufaq.com'
    elif eleccion == 5:
        enlace = '/images'
        imagen = 'galeria'
        mensaje = 'Nueva galer&iacute;a de im&aacute;genes (beta)'
    else:
        enlace = '/actualidad#nuevo-enlace'
        imagen = 'traje-anonymous'
        mensaje = 'Anonymous tambi&eacute;n comparte enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc.'
    
    return '<a href="' + enlace + '"><img src="/img/' + imagen + '.png" alt="' + imagen + '" title="' + mensaje + '"/></a>'


register.filter( cortamail )
register.filter( avatar )
register.filter( karmsg )
register.filter( puntos )
register.filter( estado_pregunta )
register.filter( randomsg )

